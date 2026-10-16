"""Tests de la base unificada de leads: normalización de país y teléfono,
categorías de interés, formulario, importación, exportación y campaña de
WhatsApp."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import CompradorForm
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
