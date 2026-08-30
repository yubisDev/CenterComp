"""Utilidades de normalización de texto para datos importados (CSV/Excel,
leads de formularios, etc.) que suelen venir en MAYÚSCULAS o minúsculas
inconsistentes."""
import re

_SUFIJOS_LEGALES = {
    'sa', 'sas', 'ltda', 'llc', 'inc', 'corp', 'co', 'ltd', 'ca', 'bv',
    'gmbh', 'sl', 'plc', 'nv', 'spa', 'srl', 'sac',
}
_CONECTORES = {'y', 'de', 'del', 'la', 'las', 'el', 'los', 'en', 'a', 'para', 'con', 'sin', 'e'}


def titulo_inteligente(texto):
    """Capitaliza cada palabra, pero preserva en mayúscula los sufijos
    legales conocidos (S.A., S.A.S., LLC, LTDA...) y deja en minúscula los
    conectores comunes (y, de, del...) salvo que sean la primera palabra.

    'SECCA ENERGY LLC' -> 'Secca Energy LLC'
    'consorcio x y omega energy' -> 'Consorcio X y Omega Energy'
    """
    if not texto:
        return texto
    palabras = texto.split(' ')
    resultado = []
    for i, palabra in enumerate(palabras):
        if not palabra:
            resultado.append(palabra)
            continue
        base = re.sub(r'[.\-&,]', '', palabra).lower()
        if base in _SUFIJOS_LEGALES:
            resultado.append(palabra.upper())
        elif base in _CONECTORES and i != 0:
            resultado.append(palabra.lower())
        else:
            resultado.append(palabra[:1].upper() + palabra[1:].lower())
    return ' '.join(resultado)
