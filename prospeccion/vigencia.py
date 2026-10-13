"""
Vigencia de las señales de venta de los proveedores.

La IA no sabe qué fecha es hoy, así que una noticia de hace años le puede
parecer "reciente". Por eso: (1) se le dice la fecha de hoy en el prompt,
(2) se le pide la fecha de cada señal, y (3) aquí, en código, se clasifica
esa fecha. No se descarta nada: se etiqueta y se ordena, y el operador decide.
"""
import re
from datetime import date

from django.conf import settings
from django.utils import timezone

RECIENTE = 'reciente'
ANTIGUA = 'antigua'
SIN_FECHA = 'sin_fecha'

ORDEN = {RECIENTE: 0, SIN_FECHA: 1, ANTIGUA: 2}

MESES = {
    'ene': 1, 'jan': 1, 'feb': 2, 'mar': 3, 'abr': 4, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'ago': 8, 'aug': 8, 'sep': 9, 'set': 9, 'oct': 10, 'nov': 11, 'dic': 12, 'dec': 12,
}


def hoy_texto():
    """'13 de octubre de 2026' — para decirle a la IA qué fecha es hoy."""
    hoy = timezone.localdate()
    nombres = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio',
               'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    return f'{hoy.day} de {nombres[hoy.month - 1]} de {hoy.year}'


def leer_fecha(texto):
    """Entiende '2026-03-15', '2026-03', '2026', 'marzo 2026', 'Mar 2026'.
    Devuelve una fecha (día 1 si no hay día) o None."""
    texto = (texto or '').strip().lower()
    m = re.search(r'(20\d\d|19\d\d)[-/.](\d{1,2})(?:[-/.](\d{1,2}))?', texto)
    if m:
        anio, mes, dia = int(m.group(1)), int(m.group(2)), int(m.group(3) or 1)
        try:
            return date(anio, mes, dia)
        except ValueError:
            return None
    m = re.search(r'([a-záéíóú]{3,})\.?\s+(?:de\s+)?(20\d\d|19\d\d)', texto)
    if m and m.group(1)[:3] in MESES:
        return date(int(m.group(2)), MESES[m.group(1)[:3]], 1)
    m = re.fullmatch(r'(20\d\d|19\d\d)', texto)
    if m:
        return date(int(m.group(1)), 1, 1)
    return None


def clasificar(fecha_texto, hoy=None):
    fecha = leer_fecha(fecha_texto)
    if not fecha:
        return SIN_FECHA
    hoy = hoy or timezone.localdate()
    meses = (hoy.year - fecha.year) * 12 + (hoy.month - fecha.month)
    # Una fecha futura (ej. un cierre anunciado para el próximo año) también cuenta como vigente.
    return RECIENTE if meses <= settings.SENAL_MESES_RECIENTE else ANTIGUA


def etiquetar_y_ordenar(empresas, hoy=None):
    """Agrega 'vigencia' a cada empresa y pone las señales recientes primero."""
    for empresa in empresas:
        empresa['vigencia'] = clasificar(empresa.get('fecha_senal'), hoy)
    return sorted(empresas, key=lambda e: ORDEN[e['vigencia']])
