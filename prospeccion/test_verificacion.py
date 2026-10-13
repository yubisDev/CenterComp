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
        self.assertTrue(e['linkedin_busqueda'])  # no confirmado: se ofrece también la búsqueda

    def test_sin_linkedin_ofrece_enlace_de_busqueda(self):
        e = v.verificar_empresa(EmpresaTests.EMPRESA, usar_red=False)
        self.assertIn('linkedin.com/search/results/companies/?keywords=PT+Ejemplo+Pelapis', e['linkedin_busqueda'])
        html = render_to_string('prospeccion/parciales/contacto_ia.html', {'empresa': e})
        self.assertIn('Buscar en LinkedIn', html)


class RedesInventadasTests(SimpleTestCase):
    EMPRESA = dict(EmpresaTests.EMPRESA, linkedin_url='https://www.linkedin.com/company/pt-ejemplo-pelapis')

    def _verificar(self, paginas):
        with mock.patch.object(v, '_dominio_recibe_correo', return_value=True), \
                mock.patch.object(v, '_pagina_responde', return_value=True):
            return v.verificar_empresa(self.EMPRESA, paginas_consultadas=paginas)

    def test_linkedin_que_google_no_cito_queda_dudoso_con_busqueda(self):
        e = self._verificar(['https://ejemplo.co.id/kontak', 'https://www.linkedin.com/company/otra-empresa'])
        self.assertEqual(e['linkedin_url'], 'https://www.linkedin.com/company/pt-ejemplo-pelapis')
        self.assertEqual(e['verificacion']['linkedin_url']['estado'], v.DUDOSO)
        self.assertNotIn('linkedin_url', e['descartados'])
        self.assertIn('keywords=PT+Ejemplo+Pelapis', e['linkedin_busqueda'])

    def test_linkedin_que_google_si_devolvio_se_verifica(self):
        e = self._verificar(['https://id.linkedin.com/company/PT-Ejemplo-Pelapis/about/'])
        self.assertEqual(e['linkedin_url'], 'https://www.linkedin.com/company/pt-ejemplo-pelapis')
        self.assertEqual(e['verificacion']['linkedin_url']['estado'], v.VERIFICADO)

    def test_sin_datos_de_paginas_no_se_juzga(self):
        e = self._verificar(None)
        self.assertEqual(e['verificacion']['linkedin_url']['estado'], v.SIN_VERIFICAR)

    def test_si_la_red_no_deja_abrir_ninguna_fuente_no_se_juzga(self):
        with mock.patch.object(v.requests, 'head', side_effect=v.requests.exceptions.SSLError('cert')):
            self.assertIsNone(v.resolver_fuentes(['https://vertexaisearch.cloud.google.com/grounding-api-redirect/1']))

    def test_resolver_fuentes(self):
        respuesta = mock.Mock(headers={'Location': 'https://www.linkedin.com/company/x'})
        with mock.patch.object(v.requests, 'head', return_value=respuesta):
            reales = v.resolver_fuentes(['https://vertexaisearch.cloud.google.com/grounding-api-redirect/1'])
        self.assertEqual(reales, ['https://www.linkedin.com/company/x'])


class PaisesTests(SimpleTestCase):
    def test_reconoce_paises_fuera_de_la_lista_manual(self):
        for nombre, codigo in [('Países Bajos', 'NL'), ('Holanda', 'NL'), ('Arabia Saudita', 'SA'),
                               ('Netherlands', 'NL'), ('Marruecos', 'MA'), ('Perú', 'PE'),
                               ('peru', 'PE'), ('USA', 'US'), ('DE', 'DE')]:
            self.assertEqual(v.codigo_pais(nombre), codigo, nombre)

    def test_numero_local_de_pais_no_listado_antes(self):
        r = v.verificar_telefono('0612345678', 'Países Bajos')
        self.assertEqual(r['estado'], v.VERIFICADO)
        self.assertEqual(r['normalizado'], '+31612345678')

    def test_pais_desconocido_sin_indicativo_no_se_descarta(self):
        r = v.verificar_telefono('612 345 678', 'Reino de Fantasía')
        self.assertEqual(r['estado'], v.SIN_VERIFICAR)

    def test_pais_desconocido_con_indicativo_si_se_verifica(self):
        r = v.verificar_telefono('+49 30 12345678', 'Reino de Fantasía')
        self.assertIn(r['estado'], (v.VERIFICADO, v.DUDOSO))


@override_settings(GEMINI_API_KEY='prueba', VERIFICACION_RED=True, BUSQUEDA_LINKEDIN=True)
class BusquedaLinkedInTests(SimpleTestCase):
    def _respuesta(self, texto, urls=()):
        chunks = [mock.Mock(web=mock.Mock(title='linkedin.com', uri=u)) for u in urls]
        metadata = mock.Mock(grounding_chunks=chunks, grounding_supports=[])
        return mock.Mock(text=texto, candidates=[mock.Mock(grounding_metadata=metadata)])

    def _buscar(self, respuestas, **ajustes):
        from . import ia_busqueda
        with mock.patch('google.genai.Client') as cliente, \
                mock.patch.object(v, '_dominio_recibe_correo', return_value=True), \
                mock.patch.object(v, '_pagina_responde', return_value=True), \
                override_settings(**ajustes):
            cliente.return_value.models.generate_content.side_effect = respuestas
            empresas, fuentes = ia_busqueda.buscar_empresas('importadores de café en Alemania')
        return cliente.return_value.models.generate_content, empresas, fuentes

    PRINCIPAL = ('[{"nombre_empresa": "Bernhard Rothfos GmbH", "pais": "Alemania", '
                 '"sitio_web": "https://rothfos.de"}, {"nombre_empresa": "Kaffee X", "pais": "Alemania"}]')

    def test_paso_dedicado_encuentra_y_confirma_el_linkedin(self):
        linkedin = 'https://de.linkedin.com/company/bernhard-rothfos-gmbh'
        llamada, empresas, fuentes = self._buscar([
            self._respuesta(self.PRINCIPAL),
            self._respuesta('[{"nombre_empresa": "Bernhard Rothfos GmbH", "linkedin_url": "%s"}, '
                            '{"nombre_empresa": "Kaffee X", "linkedin_url": ""}]' % linkedin, urls=[linkedin]),
        ])
        self.assertEqual(llamada.call_count, 2)
        rothfos, kaffee = empresas
        self.assertEqual(rothfos['linkedin_url'], linkedin)
        self.assertEqual(rothfos['verificacion']['linkedin_url']['estado'], v.VERIFICADO)
        self.assertEqual(rothfos['linkedin_busqueda'], '')
        self.assertEqual(kaffee['linkedin_url'], '')
        self.assertTrue(kaffee['linkedin_busqueda'])

    def test_si_el_paso_de_linkedin_falla_la_busqueda_sigue(self):
        llamada, empresas, _ = self._buscar([self._respuesta(self.PRINCIPAL), RuntimeError('cuota agotada')])
        self.assertEqual(len(empresas), 2)

    def test_desactivado_no_hace_llamada_extra(self):
        llamada, empresas, _ = self._buscar([self._respuesta(self.PRINCIPAL)], BUSQUEDA_LINKEDIN=False)
        self.assertEqual(llamada.call_count, 1)

    def test_linkedin_armado_sin_respaldo_queda_dudoso(self):
        _, empresas, _ = self._buscar([
            self._respuesta(self.PRINCIPAL),
            self._respuesta('[{"nombre_empresa": "Kaffee X", "linkedin_url": "https://www.linkedin.com/company/kaffee-x"}]',
                            urls=['https://kaffee-x.de/']),
        ])
        self.assertEqual(empresas[1]['verificacion']['linkedin_url']['estado'], v.DUDOSO)


class VigenciaTests(SimpleTestCase):
    def test_leer_fechas_en_varios_formatos(self):
        from datetime import date
        from . import vigencia
        self.assertEqual(vigencia.leer_fecha('2026-03-15'), date(2026, 3, 15))
        self.assertEqual(vigencia.leer_fecha('2025-11'), date(2025, 11, 1))
        self.assertEqual(vigencia.leer_fecha('marzo de 2024'), date(2024, 3, 1))
        self.assertEqual(vigencia.leer_fecha('Mar 2024'), date(2024, 3, 1))
        self.assertEqual(vigencia.leer_fecha('2021'), date(2021, 1, 1))
        self.assertIsNone(vigencia.leer_fecha(''))
        self.assertIsNone(vigencia.leer_fecha('hace poco'))

    @override_settings(SENAL_MESES_RECIENTE=12)
    def test_clasificar_y_ordenar(self):
        from datetime import date
        from . import vigencia
        hoy = date(2026, 10, 13)
        empresas = [{'nombre_empresa': 'Vieja', 'fecha_senal': '2021-05'},
                    {'nombre_empresa': 'Sin', 'fecha_senal': ''},
                    {'nombre_empresa': 'Nueva', 'fecha_senal': '2026-08-02'},
                    {'nombre_empresa': 'Futura', 'fecha_senal': '2027-01'}]
        orden = vigencia.etiquetar_y_ordenar(empresas, hoy)
        self.assertEqual([e['nombre_empresa'] for e in orden], ['Nueva', 'Futura', 'Sin', 'Vieja'])
        self.assertEqual([e['vigencia'] for e in orden], ['reciente', 'reciente', 'sin_fecha', 'antigua'])

    @override_settings(GEMINI_API_KEY='prueba', VERIFICACION_RED=False, BUSQUEDA_LINKEDIN=False)
    def test_prompt_lleva_la_fecha_de_hoy_y_proveedores_se_ordenan(self):
        from . import ia_busqueda
        texto = ('[{"nombre_empresa": "Vieja SA", "pais": "Perú", "fecha_senal": "2019-02"},'
                 ' {"nombre_empresa": "Nueva SA", "pais": "Perú", "fecha_senal": "%s"}]'
                 % __import__('django.utils.timezone', fromlist=['x']).localdate().isoformat())
        with mock.patch('google.genai.Client') as cliente:
            cliente.return_value.models.generate_content.return_value = mock.Mock(text=texto, candidates=[])
            empresas, _ = ia_busqueda.buscar_proveedores('minería cerrando en Perú')
        prompt = cliente.return_value.models.generate_content.call_args.kwargs['contents']
        from . import vigencia
        self.assertIn(f'Hoy es {vigencia.hoy_texto()}', prompt)
        self.assertEqual([e['nombre_empresa'] for e in empresas], ['Nueva SA', 'Vieja SA'])
        self.assertEqual(empresas[1]['vigencia'], 'antigua')


class MarcarContactadoTests(TestCase):
    def setUp(self):
        self.client.force_login(get_user_model().objects.create_user('op9', password='x'))

    def test_boton_solo_para_por_contactar_y_sin_historial_repetido(self):
        from .models import HistorialContacto
        c = Comprador.objects.create(nombre_empresa='ACME', pais='Perú')
        lista = self.client.get(reverse('compradores_lista')).content.decode()
        self.assertIn('Marcar ACME como contactado', lista)

        url = reverse('comprador_marcar_contactado', args=[c.pk])
        self.client.post(url)
        self.client.post(url)  # segundo clic (p. ej. pestaña vieja)
        c.refresh_from_db()
        self.assertEqual(c.estado, Comprador.Estado.CONTACTADO)
        self.assertEqual(HistorialContacto.objects.filter(comprador=c).count(), 1)

        lista = self.client.get(reverse('compradores_lista')).content.decode()
        self.assertNotIn('Marcar ACME como contactado', lista)

    def test_no_redirige_a_otro_sitio(self):
        c = Comprador.objects.create(nombre_empresa='ACME', pais='Perú')
        r = self.client.post(reverse('comprador_marcar_contactado', args=[c.pk]), {'next': 'https://malicioso.com/'})
        self.assertEqual(r.url, reverse('compradores_lista'))
