from django import template
from django.utils import timezone
from django.utils.timesince import timesince

register = template.Library()


@register.filter
def hace(fecha):
    if not fecha:
        return 'Nunca'
    delta = timezone.now() - fecha
    if delta.total_seconds() < 60:
        return 'Justo ahora'
    return f'{timesince(fecha)} atrás'
