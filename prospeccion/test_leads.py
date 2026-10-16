"""Tests de la base unificada de leads: normalización de país y teléfono,
categorías de interés, formulario, importación, exportación y campaña de
WhatsApp."""
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .forms import CompradorForm
from .importacion import procesar_importacion
from .models import CategoriaInteres, Comprador, PlantillaMensaje
from .normalizacion import normalizar_pais, normalizar_telefono, pais_desde_telefono


class NormalizacionTests(TestCase):
    def test_pais_variantes_quedan_iguales(self):
        for texto in ('panama', 'PANAMÁ', 'Panamá ', 'PA'):
            self.assertEqual(normalizar_pais(texto), 'Panamá', texto)
        self.assertEqual(normalizar_pais('colombia'), 'Colombia')
        self.assertEqual(normalizar_pais(''), '')

    def test_telefono_colombiano_sin_indicativo(self):
        self.assertEqual(normalizar_telefono('300 123 4567'), '573001234567')

    def test_telefono_formato_meta_lead_ads(self):
        self.assertEqual(normalizar_telefono('p:+573001234567'), '573001234567')

    def test_telefono_panameno(self):
        self.assertEqual(normalizar_telefono('6123-4567'), '50761234567')
        self.assertEqual(normalizar_telefono('+507 6123 4567'), '50761234567')

    def test_telefono_con_indicativo_sin_mas(self):
        self.assertEqual(normalizar_telefono('573001234567'), '573001234567')

    def test_pais_desde_telefono(self):
        self.assertEqual(pais_desde_telefono('+507 6123 4567'), 'Panamá')
        self.assertEqual(pais_desde_telefono('123'), '')


class CompradorLeadTests(TestCase):
    def test_categorias_iniciales_creadas_por_migracion(self):
        nombres = set(CategoriaInteres.objects.values_list('nombre', flat=True))
        self.assertTrue({
            'Vehículos de subasta', 'Excedentes industriales', 'Inmuebles', 'Revestimientos / construcción',
        } <= nombres)

    def test_save_normaliza_pais_y_telefono(self):
        c = Comprador.objects.create(nombre_contacto='Ana Pérez', pais='panama', telefono='6123 4567')
        self.assertEqual(c.pais, 'Panamá')
        self.assertEqual(c.telefono_normalizado, '50761234567')
        self.assertEqual(c.whatsapp_numero, '50761234567')

    def test_pais_se_deduce_del_telefono(self):
        c = Comprador.objects.create(nombre_contacto='Luis', telefono='+507 6123 4567')
        self.assertEqual(c.pais, 'Panamá')

    def test_nombre_mostrar_y_saludo(self):
        persona = Comprador(nombre_contacto='Ana')
        empresa = Comprador(nombre_empresa='Acme', nombre_contacto='Ana')
        self.assertEqual(persona.nombre_mostrar, 'Ana')
        self.assertEqual(empresa.nombre_mostrar, 'Acme')
        self.assertEqual(empresa.nombre_saludo, 'Ana')

    def test_fecha_acepta_se_registra_y_se_borra(self):
        c = Comprador.objects.create(nombre_contacto='Ana', acepta_mensajes=True)
        self.assertIsNotNone(c.fecha_acepta)
        c.acepta_mensajes = False
        c.save()
        self.assertIsNone(c.fecha_acepta)

    def test_plantilla_usa_nombre_y_categoria(self):
        c = Comprador.objects.create(nombre_contacto='Ana', telefono='3001234567')
        c.categorias_interes.add(CategoriaInteres.objects.get(nombre='Inmuebles'))
        plantilla = PlantillaMensaje.objects.create(
            nombre='WA', tipo=PlantillaMensaje.Tipo.WHATSAPP, cuerpo='Hola {nombre}, novedades de {categoria}',
        )
        _, cuerpo = plantilla.render(c)
        self.assertEqual(cuerpo, 'Hola Ana, novedades de Inmuebles')


class CompradorFormTests(TestCase):
    def _datos(self, **extra):
        datos = {'fuente': 'whatsapp', 'estado': 'por_contactar'}
        datos.update(extra)
        return datos

    def test_exige_algun_nombre(self):
        form = CompradorForm(data=self._datos(telefono='3001234567'))
        self.assertFalse(form.is_valid())
        self.assertIn('al menos el nombre', str(form.non_field_errors()))

    def test_acepta_solo_nombre_de_contacto(self):
        form = CompradorForm(data=self._datos(nombre_contacto='Ana', telefono='3001234567'))
        self.assertTrue(form.is_valid(), form.errors)

    def test_rechaza_telefono_duplicado_aunque_este_escrito_distinto(self):
        Comprador.objects.create(nombre_contacto='Ana', telefono='+57 300 123 4567')
        form = CompradorForm(data=self._datos(nombre_contacto='Ana 2', telefono='3001234567'))
        self.assertFalse(form.is_valid())
        self.assertIn('ya está registrado', str(form.errors['telefono']))

    def test_editar_el_mismo_registro_no_es_duplicado(self):
        c = Comprador.objects.create(nombre_contacto='Ana', telefono='3001234567')
        form = CompradorForm(data=self._datos(nombre_contacto='Ana', telefono='3001234567'), instance=c)
        self.assertTrue(form.is_valid(), form.errors)


class LoginMixin:
    def setUp(self):
        self.usuario = get_user_model().objects.create_user('operador', password='clave-segura-123')
        self.client.login(username='operador', password='clave-segura-123')


class CompradorFormVistaTests(LoginMixin, TestCase):
    def test_crear_lead_con_categorias(self):
        cat = CategoriaInteres.objects.get(nombre='Revestimientos / construcción')
        respuesta = self.client.post(reverse('comprador_nuevo'), {
            'nombre_contacto': 'Carlos', 'telefono': '6123 4567', 'fuente': 'meta_ads',
            'campana': 'Revestimientos PA', 'estado': 'por_contactar',
            'categorias_interes': [cat.pk], 'acepta_mensajes': 'on',
        })
        self.assertEqual(respuesta.status_code, 302)
        c = Comprador.objects.get(nombre_contacto='Carlos')
        self.assertEqual(c.pais, 'Panamá')
        self.assertEqual(list(c.categorias_interes.all()), [cat])
        self.assertTrue(c.acepta_mensajes)


def _csv(contenido, nombre='leads.csv', codificacion='utf-8'):
    return SimpleUploadedFile(nombre, contenido.encode(codificacion), content_type='text/csv')


class ImportacionLeadsTests(TestCase):
    def test_csv_meta_lead_ads_utf16_tabulado(self):
        contenido = (
            'id\tcreated_time\tad_name\tcampaign_name\tplatform\tis_organic\t'
            '¿qué_producto_te_interesa?\tfull_name\temail\tphone_number\n'
            'l:1\t2026-10-01\tAnuncio 1\tRevestimientos Panamá\tig\tfalse\t'
            'porcelanato\tmaria lopez\tmaria@ejemplo.com\tp:+50761234567\n'
            'l:2\t2026-10-02\tAnuncio 2\tSubasta carros\tfb\tfalse\t'
            'una camioneta\tJUAN GÓMEZ\t\tp:+573001234567\n'
        )
        archivo = SimpleUploadedFile('meta.csv', b'\xff\xfe' + contenido.encode('utf-16-le'))
        resumen = procesar_importacion(archivo)
        self.assertTrue(resumen['meta'])
        self.assertEqual(resumen['creados'], 2, resumen)

        maria = Comprador.objects.get(telefono_normalizado='50761234567')
        self.assertEqual(maria.nombre_contacto, 'Maria Lopez')
        self.assertEqual(maria.pais, 'Panamá')
        self.assertEqual(maria.fuente, Comprador.Fuente.INSTAGRAM_ADS)
        self.assertEqual(maria.campana, 'Revestimientos Panamá')
        self.assertEqual([c.nombre for c in maria.categorias_interes.all()], ['Revestimientos / construcción'])

        juan = Comprador.objects.get(telefono_normalizado='573001234567')
        self.assertEqual(juan.nombre_contacto, 'Juan Gómez')
        self.assertEqual(juan.fuente, Comprador.Fuente.FACEBOOK_ADS)
        self.assertEqual([c.nombre for c in juan.categorias_interes.all()], ['Vehículos de subasta'])

    def test_csv_con_punto_y_coma_de_excel_en_espanol(self):
        resumen = procesar_importacion(_csv('nombre;telefono;pais\nAna;6123 4567;panama\n'))
        self.assertEqual(resumen['creados'], 1, resumen)
        self.assertEqual(Comprador.objects.get().pais, 'Panamá')

    def test_mismo_telefono_escrito_distinto_no_duplica_y_fusiona(self):
        cat = CategoriaInteres.objects.get(nombre='Inmuebles')
        existente = Comprador.objects.create(nombre_contacto='Ana', telefono='3001234567', fuente='whatsapp')
        resumen = procesar_importacion(_csv(
            'nombre,telefono,email,fuente,categoria\n'
            'Ana Pérez,+57 300 123 4567,ana@ejemplo.com,instagram,apartamento\n'
        ))
        self.assertEqual(resumen['creados'], 0)
        self.assertEqual(resumen['actualizados'], 1)
        self.assertEqual(Comprador.objects.count(), 1)
        existente.refresh_from_db()
        self.assertEqual(existente.nombre_contacto, 'Ana')  # no pisa lo que ya había
        self.assertEqual(existente.email, 'ana@ejemplo.com')  # completa lo vacío
        self.assertIn(cat, existente.categorias_interes.all())
        self.assertIn('volvió a llegar por Instagram', existente.notas)

    def test_reimportar_el_mismo_archivo_no_cambia_nada(self):
        contenido = 'nombre,telefono,fuente\nAna,3001234567,whatsapp\n'
        procesar_importacion(_csv(contenido))
        resumen = procesar_importacion(_csv(contenido))
        self.assertEqual(resumen['sin_cambios'], 1)
        self.assertEqual(Comprador.objects.count(), 1)

    def test_valores_por_defecto_del_formulario(self):
        cat = CategoriaInteres.objects.get(nombre='Revestimientos / construcción')
        resumen = procesar_importacion(
            _csv('telefono\n61234567\n62345678\n'),
            fuente_defecto=Comprador.Fuente.WHATSAPP, campana_defecto='Etiqueta revestimientos',
            categorias_defecto=[cat], acepta_defecto=True,
        )
        self.assertEqual(resumen['creados'], 2, resumen)
        for c in Comprador.objects.all():
            self.assertEqual(c.fuente, Comprador.Fuente.WHATSAPP)
            self.assertEqual(c.pais, 'Panamá')
            self.assertTrue(c.acepta_mensajes)
            self.assertEqual(list(c.categorias_interes.all()), [cat])

    def test_interes_sin_categoria_queda_en_notas(self):
        procesar_importacion(_csv('nombre,telefono,interes\nAna,3001234567,joyas antiguas\n'))
        c = Comprador.objects.get()
        self.assertFalse(c.categorias_interes.exists())
        self.assertIn('joyas antiguas', c.notas)

    def test_fila_sin_nombre_ni_telefono_se_reporta(self):
        resumen = procesar_importacion(_csv('nombre,email\n,sin@ejemplo.com\nAna,ana@ejemplo.com\n'))
        self.assertEqual(resumen['creados'], 1)
        self.assertEqual(len(resumen['errores']), 1)
        self.assertIn('Fila 2', resumen['errores'][0])

    def test_excel_con_telefono_numerico(self):
        import io

        import openpyxl
        wb = openpyxl.Workbook()
        wb.active.append(['Nombre', 'Teléfono', 'País'])
        wb.active.append(['Luis', 3001234567, 'Colombia'])
        salida = io.BytesIO()
        wb.save(salida)
        archivo = SimpleUploadedFile('leads.xlsx', salida.getvalue())
        resumen = procesar_importacion(archivo)
        self.assertEqual(resumen['creados'], 1, resumen)
        self.assertEqual(Comprador.objects.get().telefono_normalizado, '573001234567')


class ImportacionVistaTests(LoginMixin, TestCase):
    def test_descargar_plantilla(self):
        respuesta = self.client.get(reverse('compradores_importar_plantilla'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn('spreadsheetml', respuesta['Content-Type'])

    def test_subir_archivo_desde_la_pantalla(self):
        respuesta = self.client.post(reverse('compradores_importar'), {
            'archivo': _csv('nombre,telefono\nAna,3001234567\n'), 'fuente': 'whatsapp',
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Resultado de la importación')
        self.assertEqual(Comprador.objects.get().fuente, 'whatsapp')


class FiltrosYExportacionTests(LoginMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.revest = CategoriaInteres.objects.get(nombre='Revestimientos / construcción')
        self.vehic = CategoriaInteres.objects.get(nombre='Vehículos de subasta')
        self.ana = Comprador.objects.create(
            nombre_contacto='Ana', telefono='6123 4567', pais='Panamá', campana='Revest PA',
            fuente='meta_ads', acepta_mensajes=True,
        )
        self.ana.categorias_interes.add(self.revest)
        self.luis = Comprador.objects.create(nombre_contacto='Luis', telefono='3001234567', pais='Colombia')
        self.luis.categorias_interes.add(self.vehic, self.revest)
        self.sin = Comprador.objects.create(nombre_empresa='Acme', email='acme@ejemplo.com', pais='Colombia')

    def _nombres(self, **params):
        respuesta = self.client.get(reverse('compradores_lista'), params)
        self.assertEqual(respuesta.status_code, 200)
        return {c.nombre_mostrar for c in respuesta.context['page_obj']}

    def test_filtro_por_categoria_y_sin_categoria(self):
        self.assertEqual(self._nombres(categoria=self.revest.pk), {'Ana', 'Luis'})
        self.assertEqual(self._nombres(categoria='sin'), {'Acme'})

    def test_filtro_por_pais_categoria_y_acepta(self):
        self.assertEqual(self._nombres(pais='Panamá', categoria=self.revest.pk, acepta='1'), {'Ana'})

    def test_buscar_por_telefono_y_campana(self):
        self.assertEqual(self._nombres(q='6123'), {'Ana'})
        self.assertEqual(self._nombres(q='revest'), {'Ana'})

    def test_resumen_de_la_base(self):
        respuesta = self.client.get(reverse('compradores_lista'))
        resumen = respuesta.context['resumen_base']
        por_cat = {c['nombre']: c['cantidad'] for c in resumen['por_categoria']}
        self.assertEqual(por_cat['Revestimientos / construcción'], 2)
        self.assertEqual(resumen['sin_categoria'], 1)

    def test_exportar_excel_respeta_filtros(self):
        import io

        import openpyxl
        respuesta = self.client.get(reverse('compradores_exportar'), {'formato': 'xlsx', 'pais': 'Panamá'})
        self.assertEqual(respuesta.status_code, 200)
        wb = openpyxl.load_workbook(io.BytesIO(respuesta.content))
        filas = list(wb.active.iter_rows(values_only=True))
        self.assertEqual(len(filas), 2)
        self.assertEqual(filas[1][0], 'Ana')
        self.assertIn('+50761234567', filas[1])
        self.assertIn('Revestimientos / construcción', filas[1])

    def test_exportar_lista_whatsapp_sin_repetidos_ni_vacios(self):
        Comprador.objects.create(nombre_empresa='Duplicado', whatsapp='+507 6123 4567', pais='Panamá')
        respuesta = self.client.get(reverse('compradores_exportar'), {'formato': 'whatsapp'})
        lineas = respuesta.content.decode('utf-8-sig').strip().splitlines()
        self.assertEqual(lineas[0], 'Nombre,Telefono,Pais,Categorias')
        numeros = [linea.split(',')[1] for linea in lineas[1:]]
        self.assertCountEqual(numeros, ['+50761234567', '+573001234567'])


class CampanaWhatsappTests(LoginMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.revest = CategoriaInteres.objects.get(nombre='Revestimientos / construcción')
        self.ana = Comprador.objects.create(nombre_contacto='Ana', telefono='6123 4567', acepta_mensajes=True)
        self.ana.categorias_interes.add(self.revest)
        self.repetida = Comprador.objects.create(nombre_contacto='Ana bis', whatsapp='+50761234567')
        self.repetida.categorias_interes.add(self.revest)
        self.col = Comprador.objects.create(nombre_contacto='Luis', telefono='3001234567')
        self.col.categorias_interes.add(self.revest)
        Comprador.objects.create(nombre_empresa='Sin teléfono', email='x@ejemplo.com', pais='Panamá')
        self.plantilla = PlantillaMensaje.objects.create(
            nombre='Promo 40', tipo=PlantillaMensaje.Tipo.WHATSAPP, cuerpo='Hola {nombre}, 40% de descuento',
        )
        self.url = reverse('compradores_campana_whatsapp')

    def test_filtra_panama_revestimientos_sin_repetir_numeros(self):
        respuesta = self.client.get(self.url, {
            'pais': 'Panamá', 'categoria': self.revest.pk, 'plantilla': self.plantilla.pk,
        })
        self.assertEqual(respuesta.status_code, 200)
        destinatarios = respuesta.context['destinatarios']
        self.assertEqual(len(destinatarios), 1)
        self.assertEqual(destinatarios[0].mensaje, 'Hola Ana, 40% de descuento')
        self.assertIn('https://wa.me/50761234567?text=Hola%20Ana', destinatarios[0].whatsapp_url)
        self.assertEqual(respuesta.context['sin_autorizacion'], 0)

    def test_avisa_contactos_sin_autorizacion(self):
        respuesta = self.client.get(self.url, {'categoria': self.revest.pk})
        self.assertEqual(respuesta.context['sin_autorizacion'], 1)
        self.assertContains(respuesta, 'no tiene registrado que aceptó')

    def test_marcar_enviado_registra_historial_una_sola_vez(self):
        datos = {'comprador_id': self.ana.pk, 'plantilla_id': self.plantilla.pk}
        url = reverse('compradores_campana_whatsapp_registrar')
        r1 = self.client.post(url, datos, HTTP_X_REQUESTED_WITH='fetch')
        r2 = self.client.post(url, datos, HTTP_X_REQUESTED_WITH='fetch')
        self.assertEqual(r1.json(), {'ok': True, 'creado': True})
        self.assertEqual(r2.json(), {'ok': True, 'creado': False})
        self.ana.refresh_from_db()
        self.assertEqual(self.ana.historial.count(), 1)
        self.assertEqual(self.ana.historial.get().medio, 'whatsapp')
        self.assertEqual(self.ana.estado, Comprador.Estado.CONTACTADO)

        respuesta = self.client.get(self.url, {'pais': 'Panamá', 'plantilla': self.plantilla.pk})
        self.assertTrue(respuesta.context['destinatarios'][0].ya_enviado)
        self.assertEqual(respuesta.context['enviados'], 1)

    def test_marcar_enviado_sin_javascript_redirige(self):
        respuesta = self.client.post(reverse('compradores_campana_whatsapp_registrar'), {
            'comprador_id': self.ana.pk, 'plantilla_id': self.plantilla.pk, 'next': self.url + '?pais=Panam%C3%A1',
        })
        self.assertRedirects(respuesta, self.url + '?pais=Panam%C3%A1', fetch_redirect_response=False)

    def test_texto_sugerido_precarga_la_plantilla(self):
        respuesta = self.client.get(reverse('plantilla_nueva'), {'tipo': 'whatsapp', 'cuerpo': 'Hola {nombre}'})
        self.assertEqual(respuesta.context['form'].initial['cuerpo'], 'Hola {nombre}')

    def test_requiere_login(self):
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, 302)
