"""
Genera un listado GRANDE de compradores ficticios del sector electrónica,
solo para probar la app con volumen real (buscador, filtros, paginación).

Estos NO son empresas reales: los correos y el sitio web usan el dominio
"example.com" (reservado por IANA para documentación, no recibe correos
reales ni resuelve a ningún sitio) y cada registro queda marcado en sus
notas como dato de prueba. No deben usarse para contactar a nadie.

Los enlaces de LinkedIn/Facebook/Instagram sí apuntan a las plataformas
reales (no existe un equivalente "reservado" para redes sociales), pero
usan handles inventados a partir de nombres de empresa ficticios — al
abrirlos, la plataforma simplemente mostrará "página no encontrada".

Uso:
    python manage.py seed_electronica_demo            # crea ~55 compradores
    python manage.py seed_electronica_demo --borrar    # elimina los de prueba
"""
import random

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from prospeccion.models import Comprador, Producto

MARCA_PRUEBA = 'Dato de prueba (ficticio) — no contactar realmente.'

PALABRAS = [
    'Voltix', 'Nexora', 'Circuitex', 'Amperia', 'Byteworks', 'Quantex',
    'Pixelnova', 'Synaptec', 'Ionix', 'Wattify', 'Chiptrade', 'Novatek',
    'Signalis', 'Fluxtronic', 'Digivex', 'Microlink', 'Sensorio', 'Radiant',
    'Powergrid', 'Streamline', 'Corelectra', 'Zentrix', 'Lumatek', 'Ohmnia',
    'Vectroni', 'Waveform', 'Brightcore', 'Neuronix', 'Kinetix', 'Solstice',
    'Primetronic', 'Andean Tech', 'Global Circuit', 'Metropolitan Electro',
    'Skyline Devices', 'Harbor Electronics', 'Union Byte', 'Pacific Volt',
]

PAISES = [
    ('Colombia', ['Bogotá', 'Medellín', 'Cali', 'Barranquilla', 'Cartagena', 'Bucaramanga'], 'S.A.S.', '+57', ['300', '301', '310', '315', '320']),
    ('México', ['Ciudad de México', 'Guadalajara', 'Monterrey'], 'S.A. de C.V.', '+52', ['55', '33', '81']),
    ('España', ['Madrid', 'Barcelona', 'Valencia'], 'S.L.', '+34', ['61', '62', '63']),
    ('Estados Unidos', ['Miami', 'Los Ángeles', 'Houston'], 'Inc.', '+1', ['305', '213', '713']),
    ('Alemania', ['Berlín', 'Múnich', 'Hamburgo'], 'GmbH', '+49', ['151', '152', '160']),
    ('Brasil', ['São Paulo', 'Río de Janeiro'], 'Ltda.', '+55', ['11', '21']),
    ('Chile', ['Santiago'], 'SpA', '+56', ['9']),
    ('Perú', ['Lima'], 'S.A.C.', '+51', ['9']),
    ('Ecuador', ['Quito', 'Guayaquil'], 'S.A.', '+593', ['9']),
    ('Panamá', ['Ciudad de Panamá'], 'S.A.', '+507', ['6']),
    ('Emiratos Árabes Unidos', ['Dubái'], 'FZE', '+971', ['50']),
    ('Reino Unido', ['Londres', 'Manchester'], 'Ltd.', '+44', ['7700', '7701']),
    ('Argentina', ['Buenos Aires'], 'S.A.', '+54', ['11']),
    ('Costa Rica', ['San José'], 'S.A.', '+506', ['8']),
    ('China', ['Shenzhen', 'Shanghái'], 'Co., Ltd.', '+86', ['138', '139']),
]

SECTORES = [
    'Electrónica de consumo', 'Componentes electrónicos', 'Electrodomésticos',
    'Audio y video', 'Dispositivos móviles y accesorios', 'Gaming y entretenimiento',
    'Wearables y smart devices', 'Iluminación LED', 'Computación y periféricos',
]

FUENTES = [
    Comprador.Fuente.PROCOLOMBIA, Comprador.Fuente.CAMARA_COMERCIO,
    Comprador.Fuente.LINKEDIN, Comprador.Fuente.MANUAL, Comprador.Fuente.APOLLO,
    Comprador.Fuente.HUNTER,
]

PRODUCTOS_DEMO = [
    ('Audífonos inalámbricos', 'Electrónica', 800),
    ('Cargadores USB-C 65W', 'Electrónica', 1500),
    ('Smartwatches deportivos', 'Electrónica', 400),
    ('Parlantes Bluetooth portátiles', 'Electrónica', 600),
    ('Cables HDMI 4K', 'Electrónica', 2000),
]


class Command(BaseCommand):
    help = 'Crea (o borra) un listado grande de compradores ficticios del sector electrónica, solo para pruebas.'

    def add_arguments(self, parser):
        parser.add_argument('--borrar', action='store_true', help='Elimina los compradores de prueba generados por este comando.')
        parser.add_argument('--cantidad', type=int, default=55, help='Cuántos compradores ficticios crear (por defecto 55).')

    def handle(self, *args, **options):
        if options['borrar']:
            eliminados, _ = Comprador.objects.filter(notas=MARCA_PRUEBA).delete()
            self.stdout.write(self.style.SUCCESS(f'Eliminados {eliminados} compradores de prueba.'))
            return

        if Comprador.objects.filter(notas=MARCA_PRUEBA).exists():
            self.stdout.write(self.style.WARNING(
                'Ya existen compradores de prueba. Corre con --borrar primero si quieres regenerarlos.'
            ))
            return

        for nombre, categoria, cantidad in PRODUCTOS_DEMO:
            Producto.objects.get_or_create(
                nombre=nombre,
                defaults={'categoria': categoria, 'cantidad_disponible': cantidad},
            )
        productos = list(Producto.objects.all())

        rng = random.Random(42)
        cantidad = options['cantidad']
        creados = 0
        intentos = 0
        usados = set()

        while creados < cantidad and intentos < cantidad * 5:
            intentos += 1
            palabra = rng.choice(PALABRAS)
            pais, ciudades, sufijo, cod_pais, prefijos = rng.choice(PAISES)
            ciudad = rng.choice(ciudades)
            sector = rng.choice(SECTORES)

            nombre_empresa = f'{palabra} {sufijo}'
            if (nombre_empresa, pais) in usados:
                continue
            usados.add((nombre_empresa, pais))

            slug = slugify(palabra)
            dominio_pais = slugify(pais).replace('-', '')[:3]
            email = f'compras@{slug}-{dominio_pais}.example.com'

            linkedin_url = f'https://www.linkedin.com/company/{slug}-{dominio_pais}' if rng.random() < 0.55 else ''
            facebook_url = f'https://www.facebook.com/{slug}{dominio_pais}' if rng.random() < 0.35 else ''
            instagram_url = f'https://www.instagram.com/{slug}{dominio_pais}' if rng.random() < 0.25 else ''
            sitio_web = f'https://{slug}.example.com' if rng.random() < 0.65 else ''

            prefijo = rng.choice(prefijos)
            numero_local = ''.join(str(rng.randint(0, 9)) for _ in range(7))
            telefono = f'{cod_pais} {prefijo} {numero_local[:3]} {numero_local[3:]}'

            estado_roll = rng.random()
            if estado_roll < 0.55:
                estado = Comprador.Estado.POR_CONTACTAR
            elif estado_roll < 0.78:
                estado = Comprador.Estado.CONTACTADO
            elif estado_roll < 0.92:
                estado = Comprador.Estado.INTERESADO
            elif estado_roll < 0.97:
                estado = Comprador.Estado.CLIENTE
            else:
                estado = Comprador.Estado.DESCARTADO

            comprador = Comprador.objects.create(
                nombre_empresa=nombre_empresa,
                pais=pais,
                ciudad=ciudad,
                sector=sector,
                email=email,
                telefono=telefono,
                linkedin_url=linkedin_url,
                facebook_url=facebook_url,
                instagram_url=instagram_url,
                sitio_web=sitio_web,
                fuente=rng.choice(FUENTES),
                estado=estado,
                notas=MARCA_PRUEBA,
            )
            comprador.productos_interes.add(rng.choice(productos))
            creados += 1

        self.stdout.write(self.style.SUCCESS(f'Creados {creados} compradores ficticios de electrónica.'))
