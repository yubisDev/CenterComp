"""Exportación de la base de leads a Excel o CSV, con los mismos filtros
del listado. El formato "whatsapp" deja solo nombre y número con indicativo,
listo para una herramienta de envío o para guardar los contactos en el
teléfono antes de armar una lista de difusión."""
import csv
import io

from django.utils import timezone

COLUMNAS = [
    ('Nombre de contacto', lambda c: c.nombre_contacto),
    ('Empresa', lambda c: c.nombre_empresa),
    ('Teléfono', lambda c: c.telefono),
    ('WhatsApp (con indicativo)', lambda c: f'+{c.whatsapp_numero}' if c.whatsapp_numero else ''),
    ('Correo', lambda c: c.email),
    ('País', lambda c: c.pais),
    ('Ciudad', lambda c: c.ciudad),
    ('Origen', lambda c: c.get_fuente_display()),
    ('Campaña', lambda c: c.campana),
    ('Categorías de interés', lambda c: ', '.join(cat.nombre for cat in c.categorias_interes.all())),
    ('Acepta promociones', lambda c: 'Sí' if c.acepta_mensajes else 'No'),
    ('Estado', lambda c: c.get_estado_display()),
    ('Sector', lambda c: c.sector),
    ('Último contacto', lambda c: timezone.localtime(c.fecha_ultimo_contacto).strftime('%d/%m/%Y') if c.fecha_ultimo_contacto else ''),
    ('Fecha de ingreso', lambda c: timezone.localtime(c.creado_en).strftime('%d/%m/%Y')),
    ('Notas', lambda c: c.notas),
]


def filas_completas(compradores):
    yield [titulo for titulo, _ in COLUMNAS]
    for c in compradores:
        yield [obtener(c) or '' for _, obtener in COLUMNAS]


def filas_whatsapp(compradores):
    """Una fila por número, sin repetidos y solo con números válidos."""
    yield ['Nombre', 'Telefono', 'Pais', 'Categorias']
    vistos = set()
    for c in compradores:
        numero = c.whatsapp_numero
        if not numero or len(numero) < 8 or numero in vistos:
            continue
        vistos.add(numero)
        yield [c.nombre_saludo or c.nombre_mostrar, f'+{numero}', c.pais,
               ', '.join(cat.nombre for cat in c.categorias_interes.all())]


def a_csv(filas):
    salida = io.StringIO()
    # BOM para que Excel abra bien las tildes; punto y coma no, porque las
    # herramientas de envío esperan coma.
    salida.write('﻿')
    escritor = csv.writer(salida)
    for fila in filas:
        escritor.writerow(fila)
    return salida.getvalue().encode('utf-8')


def a_excel(filas, titulo_hoja='Leads'):
    import openpyxl
    from openpyxl.styles import Font
    from openpyxl.utils import get_column_letter

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = titulo_hoja
    anchos = {}
    for i, fila in enumerate(filas):
        ws.append(fila)
        for j, valor in enumerate(fila, start=1):
            anchos[j] = min(max(anchos.get(j, 10), len(str(valor)) + 2), 50)
    for celda in ws[1]:
        celda.font = Font(bold=True)
    for j, ancho in anchos.items():
        ws.column_dimensions[get_column_letter(j)].width = ancho
    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = ws.dimensions
    salida = io.BytesIO()
    wb.save(salida)
    return salida.getvalue()
