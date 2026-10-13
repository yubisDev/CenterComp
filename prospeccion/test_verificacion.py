from unittest import mock

from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.test import TestCase, SimpleTestCase, override_settings
from django.urls import reverse

from . import verificacion as v
from .models import BusquedaIA, Comprador


class TelefonoTests(SimpleTestCase):
    def test_movil_indonesio_valido(self):
        r = v.verificar_telefono('0812-3456-7890', 'Indonesia')
        self.assertEqual(r['estado'], v.VERIFICADO)
        self.assertEqual(r['normalizado'], '+6281234567890')
        self.assertTrue(r['es_movil'])

    def test_fijo_de_yakarta_valido(self):
        r = v.verificar_telefono('+62 21 5795 1234', 'Indonesia')
        self.assertEqual(r['estado'], v.VERIFICADO)
        self.assertFalse(r['es_movil'])

    def test_numero_demasiado_corto_se_descarta(self):
        self.assertEqual(v.verificar_telefono('+62 21 123', 'Indonesia')['estado'], v.DESCARTADO)

    def test_texto_que_no_es_numero_se_descarta(self):
        self.assertEqual(v.verificar_telefono('llamar a ventas', 'Indonesia')['estado'], v.DESCARTADO)

    def test_numero_de_otro_pais_es_dudoso(self):
        r = v.verificar_telefono('+57 300 1234567', 'Indonesia')
        self.assertEqual(r['estado'], v.DUDOSO)


class EmailTests(SimpleTestCase):
    def test_dominio_inexistente_se_descarta(self):
        with mock.patch.object(v, '_dominio_recibe_correo', return_value=False):
            r = v.verificar_email('ventas@revestimientos-jakarta-falso.co.id')
        self.assertEqual(r['estado'], v.DESCARTADO)

    def test_dominio_distinto_al_sitio_es_dudoso(self):
        with mock.patch.object(v, '_dominio_recibe_correo', return_value=True):
            r = v.verificar_email('info@otra.com', 'https://www.empresa.co.id')
        self.assertEqual(r['estado'], v.DUDOSO)

    def test_correo_corporativo_coincide(self):
        with mock.patch.object(v, '_dominio_recibe_correo', return_value=True):
            r = v.verificar_email('sales@empresa.co.id', 'https://www.empresa.co.id/kontak')
        self.assertEqual(r['estado'], v.VERIFICADO)

    def test_sin_red_queda_sin_verificar(self):
        with mock.patch.object(v, '_dominio_recibe_correo', return_value=None):
            self.assertEqual(v.verificar_email('a@empresa.com')['estado'], v.SIN_VERIFICAR)


class UrlTests(SimpleTestCase):
    def test_pagina_inexistente_se_descarta(self):
        with mock.patch.object(v, '_pagina_responde', return_value=False):
            self.assertEqual(v.verificar_url('www.no-existe.co.id')['estado'], v.DESCARTADO)

    def test_linkedin_de_persona_es_dudoso(self):
        r = v.verificar_url('https://www.linkedin.com/in/juan-perez', 'linkedin_url')
        self.assertEqual(r['estado'], v.DUDOSO)

    def test_linkedin_generico_se_descarta(self):
        r = v.verificar_url('https://www.linkedin.com/', 'linkedin_url')
        self.assertEqual(r['estado'], v.DESCARTADO)

    def test_facebook_que_no_es_facebook_se_descarta(self):
        r = v.verificar_url('https://empresa.com/facebook', 'facebook_url')
        self.assertEqual(r['estado'], v.DESCARTADO)


class EmpresaTests(SimpleTestCase):
    EMPRESA = {
        'nombre_empresa': 'PT Ejemplo Pelapis', 'pais': 'Indonesia',
        'email': 'sales@ejemplo.co.id', 'telefono': '0812-3456-7890', 'whatsapp': '',
        'sitio_web': 'https://ejemplo.co.id', 'linkedin_url': '', 'facebook_url': '',
        'instagram_url': '',
    }

    def test_dato_sin_respaldo_baja_a_dudoso(self):
        with mock.patch.object(v, '_dominio_recibe_correo', return_value=True), \
                mock.patch.object(v, '_pagina_responde', return_value=True):
            e = v.verificar_empresa(self.EMPRESA, texto_respaldado='PT Ejemplo, sales@ejemplo.co.id')
        self.assertEqual(e['verificacion']['email']['estado'], v.VERIFICADO)
        self.assertEqual(e['verificacion']['telefono']['estado'], v.DUDOSO)  # el número no estaba en la fuente
        self.assertTrue(e['whatsapp_posible'])

    def test_datos_inventados_se_borran(self):
        inventada = dict(self.EMPRESA, telefono='+62 21 99', sitio_web='https://inventada.co.id')
        with mock.patch.object(v, '_dominio_recibe_correo', return_value=False), \
                mock.patch.object(v, '_pagina_responde', return_value=False):
            e = v.verificar_empresa(inventada)
        self.assertEqual(e['telefono'], '')
        self.assertEqual(e['email'], '')
        self.assertEqual(e['sitio_web'], '')
        self.assertEqual(set(e['descartados']), {'telefono', 'email', 'sitio_web'})
        self.assertFalse(e['whatsapp_posible'])

    def test_plantilla_muestra_etiquetas(self):
        with mock.patch.object(v, '_dominio_recibe_correo', return_value=True), \
                mock.patch.object(v, '_pagina_responde', return_value=True):
            e = v.verificar_empresa(self.EMPRESA)
        html = render_to_string('prospeccion/parciales/contacto_ia.html', {'empresa': e})
        self.assertIn('Verificado', html)
        self.assertIn('Posible WhatsApp', html)


class GuardarTests(TestCase):
    def test_guardar_incluye_whatsapp_y_notas_de_verificacion(self):
        usuario = get_user_model().objects.create_user('op', password='x')
        self.client.force_login(usuario)
        item = v.verificar_empresa(
            dict(EmpresaTests.EMPRESA, whatsapp='+62 812 9999 8888', email='x@gmail.com'),
            usar_red=False,
        )
        item['descartados'] = {'sitio_web': 'https://inventada.co.id'}
        item['verificacion']['sitio_web'] = {'estado': 'descartado', 'motivo': 'La página no existe'}
        b = BusquedaIA.objects.create(consulta='x', usuario=usuario, estado=BusquedaIA.Estado.LISTO,
                                      resultados_json=[item])
        sesion = self.client.session
        sesion['ia_busqueda_id'] = b.pk
        sesion.save()
        self.client.post(reverse('compradores_buscar_ia_guardar'), {'seleccion': ['0']})
        c = Comprador.objects.get()
        self.assertEqual(c.whatsapp, '+6281299998888')
        self.assertEqual(c.whatsapp_numero, '6281299998888')
        self.assertIn('Sitio web descartado', c.notas)


class CacheBusquedaTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user('op2', password='x')
        self.client.force_login(self.usuario)

    def test_busqueda_identica_se_reutiliza_sin_llamar_a_la_ia(self):
        previa = BusquedaIA.objects.create(
            consulta='Revestimientos en Indonesia', usuario=self.usuario,
            estado=BusquedaIA.Estado.LISTO, resultados=1, resultados_json=[{'nombre_empresa': 'PT X'}],
        )
        with mock.patch('prospeccion.views.threading.Thread') as hilo:
            self.client.post(reverse('compradores_buscar_ia_ejecutar'),
                             {'consulta': 'revestimientos en indonesia'})
        hilo.assert_not_called()
        self.assertEqual(self.client.session['ia_busqueda_id'], previa.pk)
        self.assertEqual(BusquedaIA.objects.count(), 1)

    @override_settings(BUSQUEDA_IA_CACHE_DIAS=0)
    def test_cache_desactivado_lanza_busqueda_nueva(self):
        BusquedaIA.objects.create(
            consulta='Revestimientos en Indonesia', usuario=self.usuario,
            estado=BusquedaIA.Estado.LISTO, resultados=1, resultados_json=[{'nombre_empresa': 'PT X'}],
        )
        with mock.patch('prospeccion.views.threading.Thread') as hilo:
            self.client.post(reverse('compradores_buscar_ia_ejecutar'),
                             {'consulta': 'Revestimientos en Indonesia'})
        hilo.assert_called_once()
        self.assertEqual(BusquedaIA.objects.count(), 2)


class NivelRazonamientoTests(SimpleTestCase):
    @override_settings(GEMINI_API_KEY='prueba', GEMINI_NIVEL_RAZONAMIENTO='low', VERIFICACION_RED=False)
    def test_se_pide_razonamiento_bajo(self):
        from google.genai import types
        from . import ia_busqueda
        respuesta = mock.Mock(text='[{"nombre_empresa": "PT X", "pais": "Indonesia"}]', candidates=[])
        with mock.patch('google.genai.Client') as cliente:
            cliente.return_value.models.generate_content.return_value = respuesta
            empresas, _ = ia_busqueda.buscar_empresas('revestimientos Indonesia')
        config = cliente.return_value.models.generate_content.call_args.kwargs['config']
        self.assertEqual(config.thinking_config.thinking_level, types.ThinkingLevel.LOW)
        self.assertEqual(empresas[0]['nombre_empresa'], 'PT X')


class LinkedInTests(SimpleTestCase):
    def test_redireccion_de_google_se_cambia_por_el_enlace_real(self):
        respuesta = mock.Mock(headers={'Location': 'https://www.linkedin.com/company/pelapis-nusantara'})
        empresa = dict(EmpresaTests.EMPRESA,
                       linkedin_url='https://vertexaisearch.cloud.google.com/grounding-api-redirect/AbC123')
        with mock.patch.object(v.requests, 'head', return_value=respuesta), \
                mock.patch.object(v, '_dominio_recibe_correo', return_value=True), \
                mock.patch.object(v, '_pagina_responde', return_value=True):
            e = v.verificar_empresa(empresa)
        self.assertEqual(e['linkedin_url'], 'https://www.linkedin.com/company/pelapis-nusantara')
        self.assertEqual(e['verificacion']['linkedin_url']['estado'], v.SIN_VERIFICAR)
        self.assertEqual(e['linkedin_busqueda'], '')

    def test_sin_linkedin_ofrece_enlace_de_busqueda(self):
        e = v.verificar_empresa(EmpresaTests.EMPRESA, usar_red=False)
        self.assertIn('linkedin.com/search/results/companies/?keywords=PT+Ejemplo+Pelapis', e['linkedin_busqueda'])
        html = render_to_string('prospeccion/parciales/contacto_ia.html', {'empresa': e})
        self.assertIn('Buscar en LinkedIn', html)
