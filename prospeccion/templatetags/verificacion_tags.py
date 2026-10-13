from django import template

register = template.Library()

ETIQUETAS = {
    'verificado': ('Verificado', 'verif-ok'),
    'dudoso': ('Dudoso', 'verif-dudoso'),
    'sin_verificar': ('Sin verificar', 'verif-pendiente'),
}


@register.inclusion_tag('prospeccion/parciales/badge_verificacion.html')
def badge_verificacion(empresa, campo):
    """Etiqueta pequeña junto a un dato de contacto encontrado por la IA."""
    resultado = (empresa.get('verificacion') or {}).get(campo) if isinstance(empresa, dict) else None
    if not resultado or resultado.get('estado') not in ETIQUETAS:
        return {'mostrar': False}
    texto, clase = ETIQUETAS[resultado['estado']]
    return {'mostrar': True, 'texto': texto, 'clase': clase, 'motivo': resultado.get('motivo', '')}
