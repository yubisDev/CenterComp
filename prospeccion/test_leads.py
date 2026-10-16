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
