"""
Match automático: cuando entra un producto nuevo (a mano o por carga masiva),
revisa qué compradores tienen palabras clave de interés que coincidan y les
avisa por correo con la plantilla existente.

Reglas duras de este módulo:
- Nunca debe tumbar el guardado del producto. Un producto se guarda igual
  aunque el envío de alertas falle por completo — todo corre en un hilo
  aparte, envuelto en try/except.
- Solo se dispara al CREAR un producto (`created=True`), nunca al editarlo,
  para no reenviar la misma alerta cada vez que alguien actualiza el precio
  o la cantidad disponible.
"""
import logging
import threading

from django.core.mail import EmailMessage, get_connection
from django.db import connections, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Comprador, HistorialContacto, PlantillaMensaje, Producto

logger = logging.getLogger(__name__)


def _buscar_compradores_interesados(producto):
    texto_producto = f'{producto.nombre} {producto.categoria} {producto.descripcion}'.lower()
    candidatos = Comprador.objects.exclude(palabras_clave_interes='').exclude(email='')

    coincidencias = []
    for comprador in candidatos:
        palabras = [p.strip().lower() for p in comprador.palabras_clave_interes.split(',') if p.strip()]
        if any(palabra in texto_producto for palabra in palabras):
            coincidencias.append(comprador)
    return coincidencias


def _procesar_match_en_segundo_plano(producto_id):
    try:
        try:
            producto = Producto.objects.get(pk=producto_id)
        except Producto.DoesNotExist:
            return

        coincidencias = _buscar_compradores_interesados(producto)
        if not coincidencias:
            return

        plantilla = PlantillaMensaje.objects.filter(tipo=PlantillaMensaje.Tipo.EMAIL).first()
        if not plantilla:
            logger.warning('Match automático: hay %d comprador(es) interesados en "%s" pero no hay '
                            'ninguna plantilla de correo configurada.', len(coincidencias), producto.nombre)
            return

        connection = get_connection()
        connection.open()
        try:
            for comprador in coincidencias:
                asunto, cuerpo = plantilla.render(comprador, producto.nombre)
                try:
                    EmailMessage(
                        subject=asunto, body=cuerpo, to=[comprador.email], connection=connection,
                    ).send()
                except Exception:
                    logger.exception('No se pudo enviar la alerta de match a %s', comprador.email)
                    continue

                HistorialContacto.objects.create(
                    comprador=comprador,
                    medio=HistorialContacto.Medio.EMAIL,
                    resultado=f'Alerta automática — producto nuevo que coincide con tu interés: "{producto.nombre}"',
                )
                comprador.fecha_ultimo_contacto = timezone.now()
                if comprador.estado == Comprador.Estado.POR_CONTACTAR:
                    comprador.estado = Comprador.Estado.CONTACTADO
                comprador.save()
        finally:
            connection.close()
    except Exception:
        logger.exception('Fallo el match automático para el producto %s', producto_id)
    finally:
        connections.close_all()


def _lanzar_hilo_match(producto_id):
    threading.Thread(
        target=_procesar_match_en_segundo_plano, args=(producto_id,), daemon=True,
    ).start()


@receiver(post_save, sender=Producto)
def notificar_match_producto_nuevo(sender, instance, created, **kwargs):
    if not created:
        return
    # on_commit, no directo: el hilo abre su propia conexión a la base, y si
    # arrancara antes de que la transacción actual confirme, podría no ver
    # todavía la fila del producto (o chocar con un bloqueo en SQLite).
    transaction.on_commit(lambda: _lanzar_hilo_match(instance.pk))
