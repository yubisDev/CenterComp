from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Comprador, HistorialContacto, PlantillaMensaje, Producto
from .texto import titulo_inteligente
from .views import _procesar_importacion


class AccesoAnonimoTests(TestCase):
    """Toda vista real del CRM debe exigir login."""

    def setUp(self):
        self.producto = Producto.objects.create(nombre='Chatarra de cobre')

    def test_vistas_protegidas_redirigen_a_login(self):
        rutas = [
            reverse('compradores_lista'),
            reverse('productos_lista'),
            reverse('productos_dashboard'),
            reverse('producto_detalle', args=[self.producto.pk]),
            reverse('compradores_envio_masivo'),
        ]
        for ruta in rutas:
            respuesta = self.client.get(ruta)
            self.assertEqual(respuesta.status_code, 302, ruta)
            self.assertIn(reverse('login'), respuesta.url, ruta)


class TituloInteligenteTests(TestCase):
    def test_preserva_sufijos_legales(self):
        self.assertEqual(titulo_inteligente('SECCA ENERGY LLC'), 'Secca Energy LLC')

    def test_minusculiza_conectores_salvo_primera_palabra(self):
        self.assertEqual(
            titulo_inteligente('consorcio x y omega energy'), 'Consorcio X y Omega Energy',
        )

    def test_texto_vacio(self):
        self.assertEqual(titulo_inteligente(''), '')


class PlantillaMensajeTests(TestCase):
    def test_render_sustituye_variables(self):
        plantilla = PlantillaMensaje.objects.create(
            nombre='Oferta',
            tipo=PlantillaMensaje.Tipo.EMAIL,
            asunto='Oferta para {nombre_empresa}',
            cuerpo='Hola {nombre_empresa}, tenemos {producto} disponible en {pais}.',
        )
        comprador = Comprador.objects.create(nombre_empresa='Acme SAS', pais='Panamá')
        asunto, cuerpo = plantilla.render(comprador, 'Cobre reciclado')
        self.assertEqual(asunto, 'Oferta para Acme SAS')
        self.assertIn('Cobre reciclado', cuerpo)
        self.assertIn('Panamá', cuerpo)

    def test_render_no_falla_si_falta_variable(self):
        plantilla = PlantillaMensaje.objects.create(
            nombre='Simple', tipo=PlantillaMensaje.Tipo.EMAIL,
            asunto='Hola {nombre_empresa}', cuerpo='{variable_inexistente} {nombre_empresa}',
        )
        comprador = Comprador.objects.create(nombre_empresa='Acme SAS', pais='Panamá')
        asunto, cuerpo = plantilla.render(comprador)
        self.assertEqual(asunto, 'Hola Acme SAS')
        self.assertEqual(cuerpo, ' Acme SAS')


class ProductoDetalleTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='ana', password='clave-segura-123')
        self.client.login(username='ana', password='clave-segura-123')
        self.producto = Producto.objects.create(nombre='Motor eléctrico industrial')
        self.comprador = Comprador.objects.create(nombre_empresa='Recicladora del Sur', pais='Panamá')

    def test_vincular_comprador_desde_producto(self):
        respuesta = self.client.post(
            reverse('producto_detalle', args=[self.producto.pk]),
            {'comprador_id': self.comprador.pk},
        )
        self.assertRedirects(respuesta, reverse('producto_detalle', args=[self.producto.pk]))
        self.assertIn(self.comprador, self.producto.compradores_interesados.all())

    def test_detalle_muestra_interesados(self):
        self.producto.compradores_interesados.add(self.comprador)
        respuesta = self.client.get(reverse('producto_detalle', args=[self.producto.pk]))
        self.assertContains(respuesta, 'Recicladora del Sur')


class EnvioMasivoTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='ana', password='clave-segura-123')
        self.client.login(username='ana', password='clave-segura-123')
        self.plantilla = PlantillaMensaje.objects.create(
            nombre='Aviso de inventario', tipo=PlantillaMensaje.Tipo.EMAIL,
            asunto='Nuevo inventario para {nombre_empresa}',
            cuerpo='Hola {nombre_empresa}, tenemos novedades.',
        )
        self.con_correo = Comprador.objects.create(
            nombre_empresa='Con Correo SAS', pais='Colombia', email='contacto@empresa-demo.example.com',
            estado=Comprador.Estado.POR_CONTACTAR,
        )
        self.sin_correo = Comprador.objects.create(nombre_empresa='Sin Correo SAS', pais='Colombia')

    def test_listado_filtrado_excluye_sin_correo(self):
        respuesta = self.client.get(reverse('compradores_envio_masivo'))
        self.assertContains(respuesta, 'Con Correo SAS')
        self.assertNotContains(respuesta, 'Sin Correo SAS')

    def test_enviar_registra_correo_historial_y_avanza_estado(self):
        respuesta = self.client.post(reverse('compradores_envio_masivo_enviar'), {
            'plantilla_id': self.plantilla.pk,
            'compradores': [self.con_correo.pk, self.sin_correo.pk],
        })
        self.assertRedirects(respuesta, reverse('compradores_lista'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['contacto@empresa-demo.example.com'])

        self.con_correo.refresh_from_db()
        self.assertEqual(self.con_correo.estado, Comprador.Estado.CONTACTADO)
        self.assertTrue(
            HistorialContacto.objects.filter(comprador=self.con_correo, medio=HistorialContacto.Medio.EMAIL).exists()
        )


class ImportacionCSVTests(TestCase):
    def test_importa_filas_validas_y_omite_sin_nombre(self):
        contenido = (
            'nombre_empresa,pais,email,fuente\r\n'
            'globex sas,Panamá,globex@empresa-demo.example.com,manual\r\n'
            ',Panamá,sinnombre@empresa-demo.example.com,manual\r\n'
        )
        archivo = SimpleUploadedFile('leads.csv', contenido.encode('utf-8'), content_type='text/csv')
        resumen = _procesar_importacion(archivo)
        self.assertEqual(resumen['creados'], 1)
        self.assertEqual(len(resumen['errores']), 1)
        self.assertTrue(Comprador.objects.filter(nombre_empresa='Globex SAS').exists())
