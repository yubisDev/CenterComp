"""Normalización de país y teléfono para los leads que llegan de distintos
canales (WhatsApp, Instagram, anuncios de Meta, página web, Excel a mano).

El mismo cliente puede llegar escrito como "panama", "PANAMÁ" o "PA", y su
número como "3001234567", "+57 300 123 4567" o "p:+573001234567" (así lo
exporta Meta Lead Ads). Para filtrar por país y detectar duplicados hay que
llevarlos todos a una sola forma."""
import re

import phonenumbers
from phonenumbers import NumberParseException
from phonenumbers.geocoder import _region_display_name

from .verificacion import codigo_pais

# Si el número viene sin indicativo y no sabemos el país, probamos con los
# dos mercados donde opera la empresa: Colombia (móviles de 10 dígitos que
# empiezan por 3) y Panamá (8 dígitos). No se cruzan entre sí.
REGIONES_POR_DEFECTO = ('CO', 'PA')


def normalizar_pais(texto):
    """'panama', 'PANAMÁ' o 'PA' -> 'Panamá'. Si no se reconoce el país, lo
    devuelve limpio (sin espacios de más y con mayúscula inicial)."""
    texto = re.sub(r'\s+', ' ', (texto or '').strip())
    if not texto:
        return ''
    region = codigo_pais(texto)
    if region:
        nombre = _region_display_name(region, 'es')
        if nombre:
            return nombre
    return texto[:1].upper() + texto[1:]


def _parsear(numero, pais=''):
    """Devuelve el número parseado y válido, o None."""
    crudo = (numero or '').strip()
    # Meta Lead Ads exporta "p:+573001234567"; quitamos cualquier prefijo que no sea número o '+'.
    crudo = re.sub(r'^[^\d+]+', '', crudo)
    digitos = re.sub(r'\D', '', crudo)
    if len(digitos) < 7:
        return None

    candidatos = []
    if crudo.startswith('+'):
        candidatos.append(('+' + digitos, None))
    elif digitos.startswith('00'):
        candidatos.append(('+' + digitos[2:], None))
    else:
        region = codigo_pais(pais)
        for reg in ([region] if region else []) + list(REGIONES_POR_DEFECTO):
            candidatos.append((digitos, reg))
        # Puede venir con indicativo pero sin el '+' (ej. "573001234567").
        candidatos.append(('+' + digitos, None))

    for texto, region in candidatos:
        try:
            parseado = phonenumbers.parse(texto, region)
        except NumberParseException:
            continue
        if phonenumbers.is_valid_number(parseado):
            return parseado
    return None


def normalizar_telefono(numero, pais=''):
    """Devuelve el número en formato internacional solo con dígitos
    (ej. '573001234567'), que es lo que necesitan wa.me y WhatsApp Business.
    Si no se logra interpretar, devuelve solo los dígitos que traiga."""
    parseado = _parsear(numero, pais)
    if parseado:
        return phonenumbers.format_number(parseado, phonenumbers.PhoneNumberFormat.E164).lstrip('+')
    return re.sub(r'\D', '', numero or '')


def pais_desde_telefono(numero, pais=''):
    """Nombre del país al que pertenece el número, o '' si no se puede saber."""
    parseado = _parsear(numero, pais)
    if not parseado:
        return ''
    region = phonenumbers.region_code_for_number(parseado)
    return (_region_display_name(region, 'es') or '') if region else ''
