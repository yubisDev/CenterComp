import os

from django import template
from django.conf import settings
from django.templatetags.static import static as static_url

register = template.Library()


@register.simple_tag
def static_v(path):
    """Como {% static %}, pero agrega ?v=<fecha de modificación> para que el
    navegador nunca sirva una versión vieja en caché después de editar el
    archivo — evita el problema de 'cambié el CSS pero se ve igual'."""
    url = static_url(path)
    try:
        full_path = os.path.join(settings.BASE_DIR, 'static', path)
        version = int(os.path.getmtime(full_path))
    except OSError:
        return url
    separator = '&' if '?' in url else '?'
    return f'{url}{separator}v={version}'
