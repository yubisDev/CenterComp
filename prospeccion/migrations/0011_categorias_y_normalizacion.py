from django.db import migrations

CATEGORIAS = [
    ('Vehículos de subasta', 'vehiculo, vehículo, carro, auto, automovil, automóvil, camion, camión, '
                             'camioneta, moto, bus, volqueta, subasta de vehiculos', 1),
    ('Excedentes industriales', 'excedente, industrial, maquinaria, chatarra, raee, inventario, '
                                'equipos, repuestos, materia prima', 2),
    ('Inmuebles', 'inmueble, casa, apartamento, apto, lote, terreno, finca, local, oficina, propiedad', 3),
    ('Revestimientos / construcción', 'revestimiento, construccion, construcción, piso, porcelanato, '
                                      'ceramica, cerámica, enchape, baldosa, material de construccion', 4),
]


def crear_categorias(apps, schema_editor):
    CategoriaInteres = apps.get_model('prospeccion', 'CategoriaInteres')
    for nombre, palabras, orden in CATEGORIAS:
        CategoriaInteres.objects.get_or_create(
            nombre=nombre, defaults={'palabras_clave': palabras, 'orden': orden},
        )


def normalizar_existentes(apps, schema_editor):
    # Los modelos históricos no tienen el save() personalizado, así que se
    # aplica la misma normalización a mano.
    from prospeccion.normalizacion import normalizar_pais, normalizar_telefono, pais_desde_telefono

    Comprador = apps.get_model('prospeccion', 'Comprador')
    for c in Comprador.objects.all().iterator():
        pais = normalizar_pais(c.pais)
        numero = c.telefono or c.whatsapp
        if not pais and numero:
            pais = pais_desde_telefono(numero)
        normalizado = normalizar_telefono(numero, pais) if numero else ''
        if pais != c.pais or normalizado != c.telefono_normalizado:
            Comprador.objects.filter(pk=c.pk).update(pais=pais, telefono_normalizado=normalizado)


class Migration(migrations.Migration):

    dependencies = [
        ('prospeccion', '0010_leads_multicanal'),
    ]

    operations = [
        migrations.RunPython(crear_categorias, migrations.RunPython.noop),
        migrations.RunPython(normalizar_existentes, migrations.RunPython.noop),
    ]
