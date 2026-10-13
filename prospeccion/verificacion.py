"""
Verificación de los datos de contacto que devuelve la IA.

Idea central: el prompt le PIDE a la IA que no invente, pero eso es solo una
sugerencia. Las garantías se ponen aquí, en código normal de Python, que
revisa cada dato ANTES de que el operador lo vea.

Cada campo termina con uno de estos estados:
- 'verificado': pasó todas las revisiones.
- 'dudoso':     puede ser real, pero algo no cuadra (se muestra con aviso).
- 'descartado': es imposible o no existe (se borra del resultado).
- 'sin_verificar': no se pudo revisar (ej. sin red); se muestra con aviso.

Nada de esto es scraping: solo se consulta el DNS de un dominio y se pregunta
si una página responde, sin leer ni guardar su contenido.
"""
import re
import socket
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

import phonenumbers
from phonenumbers import NumberParseException, PhoneNumberType

try:  # dnspython es opcional: sin él se usa una revisión más simple
    import dns.exception
    import dns.resolver
except ImportError:  # pragma: no cover
    dns = None

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None

VERIFICADO = 'verificado'
DUDOSO = 'dudoso'
DESCARTADO = 'descartado'
SIN_VERIFICAR = 'sin_verificar'

TIMEOUT_RED = 4  # segundos por cada revisión de red

# La IA devuelve el país como texto libre ("Indonesia", "México", "USA"...).
# phonenumbers necesita el código ISO de 2 letras para leer números locales.
PAISES_ISO = {
    'colombia': 'CO', 'indonesia': 'ID', 'mexico': 'MX', 'méxico': 'MX',
    'estados unidos': 'US', 'usa': 'US', 'eeuu': 'US', 'united states': 'US',
    'panama': 'PA', 'panamá': 'PA', 'peru': 'PE', 'perú': 'PE',
    'ecuador': 'EC', 'chile': 'CL', 'argentina': 'AR', 'brasil': 'BR',
    'brazil': 'BR', 'venezuela': 'VE', 'costa rica': 'CR', 'guatemala': 'GT',
    'españa': 'ES', 'spain': 'ES', 'china': 'CN', 'india': 'IN',
    'vietnam': 'VN', 'tailandia': 'TH', 'thailand': 'TH', 'malasia': 'MY',
    'malaysia': 'MY', 'filipinas': 'PH', 'philippines': 'PH',
    'turquia': 'TR', 'turquía': 'TR', 'turkey': 'TR', 'alemania': 'DE',
    'germany': 'DE', 'italia': 'IT', 'italy': 'IT', 'francia': 'FR',
    'france': 'FR', 'reino unido': 'GB', 'united kingdom': 'GB',
    'emiratos arabes unidos': 'AE', 'emiratos árabes unidos': 'AE', 'uae': 'AE',
    'canada': 'CA', 'canadá': 'CA', 'corea del sur': 'KR', 'south korea': 'KR',
    'japon': 'JP', 'japón': 'JP', 'japan': 'JP',
}

CORREOS_GRATUITOS = {
    'gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com', 'live.com',
    'icloud.com', 'aol.com', 'yahoo.co.id', 'protonmail.com',
}

PATRON_EMAIL = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')


def _resultado(estado, motivo='', **extra):
    return {'estado': estado, 'motivo': motivo, **extra}


def _dominio(url_o_email):
    """'https://www.Empresa.co.id/contacto' -> 'empresa.co.id'"""
    texto = (url_o_email or '').strip().lower()
    if '@' in texto and '://' not in texto:
        host = texto.rsplit('@', 1)[1]
    else:
        if '://' not in texto:
            texto = 'http://' + texto
        host = urlparse(texto).hostname or ''
    return host[4:] if host.startswith('www.') else host


def codigo_pais(pais):
    return PAISES_ISO.get((pais or '').strip().lower())


# ---------------------------------------------------------------- teléfonos

def verificar_telefono(numero, pais=''):
    """Revisa que el número tenga una estructura posible y válida para su país.
    No prueba que alguien conteste, pero atrapa los números con longitud o
    prefijo imposibles, que es como suelen verse los inventados."""
    if not numero:
        return None
    region = codigo_pais(pais)
    try:
        parseado = phonenumbers.parse(numero, region)
    except NumberParseException:
        return _resultado(DESCARTADO, 'No tiene forma de número telefónico')

    if not phonenumbers.is_possible_number(parseado):
        return _resultado(DESCARTADO, 'Longitud imposible para ese país')
    if not phonenumbers.is_valid_number(parseado):
        return _resultado(DESCARTADO, 'Prefijo o número que no existe en el plan de numeración')

    normalizado = phonenumbers.format_number(parseado, phonenumbers.PhoneNumberFormat.E164)
    tipo = phonenumbers.number_type(parseado)
    es_movil = tipo in (PhoneNumberType.MOBILE, PhoneNumberType.FIXED_LINE_OR_MOBILE)

    region_numero = phonenumbers.region_code_for_number(parseado)
    if region and region_numero and region_numero != region:
        return _resultado(
            DUDOSO, f'El número es de {region_numero}, pero la empresa dice estar en {pais}',
            normalizado=normalizado, es_movil=es_movil,
        )
    return _resultado(VERIFICADO, 'Formato válido' + (' (móvil)' if es_movil else ''),
                      normalizado=normalizado, es_movil=es_movil)


# ------------------------------------------------------------------ correos

def _dominio_recibe_correo(dominio):
    """True si el dominio puede recibir correo, False si no existe,
    None si no se pudo comprobar (sin red, DNS caído...)."""
    if dns is not None:
        resolver = dns.resolver.Resolver()
        resolver.lifetime = TIMEOUT_RED
        for tipo in ('MX', 'A'):  # sin MX, muchos servidores usan el registro A
            try:
                resolver.resolve(dominio, tipo)
                return True
            except dns.resolver.NXDOMAIN:
                return False
            except (dns.resolver.NoAnswer, dns.resolver.NoNameservers):
                continue
            except dns.exception.DNSException:
                return None
        return False
    try:
        socket.getaddrinfo(dominio, None)
        return True
    except socket.gaierror:
        return None


def verificar_email(email, sitio_web=''):
    if not email:
        return None
    email = email.strip()
    if not PATRON_EMAIL.match(email):
        return _resultado(DESCARTADO, 'No tiene forma de correo')

    dominio = _dominio(email)
    existe = _dominio_recibe_correo(dominio)
    if existe is False:
        return _resultado(DESCARTADO, f'El dominio {dominio} no existe o no recibe correo')
    if existe is None:
        return _resultado(SIN_VERIFICAR, 'No se pudo consultar el dominio')

    if dominio in CORREOS_GRATUITOS:
        return _resultado(DUDOSO, 'Es un correo gratuito, no corporativo')
    dominio_web = _dominio(sitio_web) if sitio_web else ''
    if dominio_web and not (dominio == dominio_web or dominio.endswith('.' + dominio_web)
                            or dominio_web.endswith('.' + dominio)):
        return _resultado(DUDOSO, f'El dominio del correo no coincide con el sitio web ({dominio_web})')
    return _resultado(VERIFICADO, 'El dominio existe y recibe correo')


# ------------------------------------------------------------ sitios y redes

REDES = {
    'linkedin_url': ('linkedin.com', ('/company/', '/school/', '/showcase/')),
    'facebook_url': ('facebook.com', ()),
    'instagram_url': ('instagram.com', ()),
}


def _pagina_responde(url):
    """True si la página existe, False si el dominio no existe o da 404/410,
    None si no se pudo comprobar."""
    if requests is None:
        return None
    try:
        r = requests.head(url, timeout=TIMEOUT_RED, allow_redirects=True,
                          headers={'User-Agent': 'Mozilla/5.0 (verificador ISYN CRM)'})
        if r.status_code in (405, 501):  # hay servidores que no aceptan HEAD
            r = requests.get(url, timeout=TIMEOUT_RED, allow_redirects=True, stream=True,
                             headers={'User-Agent': 'Mozilla/5.0 (verificador ISYN CRM)'})
            r.close()
    except requests.exceptions.ConnectionError as exc:
        # "Name or service not known" = el dominio no existe
        if 'resolve' in str(exc).lower() or 'name or service' in str(exc).lower():
            return False
        return None
    except requests.exceptions.RequestException:
        return None
    if r.status_code in (404, 410):
        return False
    return True  # 2xx, 3xx, 401, 403, 999 (LinkedIn bloquea bots) => la página existe


def verificar_url(url, campo='sitio_web'):
    if not url:
        return None
    url = url.strip()
    if not url.lower().startswith(('http://', 'https://')):
        url = 'https://' + url
    host = _dominio(url)
    if not host or '.' not in host:
        return _resultado(DESCARTADO, 'No es una dirección web válida')

    if campo in REDES:
        dominio_red, rutas_empresa = REDES[campo]
        if not (host == dominio_red or host.endswith('.' + dominio_red)):
            return _resultado(DESCARTADO, f'No es un enlace de {dominio_red}')
        ruta = urlparse(url).path.lower()
        if ruta in ('', '/'):
            return _resultado(DESCARTADO, 'Es la página principal de la red, no de la empresa')
        if rutas_empresa and not ruta.startswith(rutas_empresa):
            return _resultado(DUDOSO, 'Parece el perfil de una persona, no de la empresa')
        # Las redes sociales bloquean las revisiones automáticas, así que aquí
        # solo validamos la forma del enlace; no podemos confirmar que exista.
        return _resultado(SIN_VERIFICAR, 'Forma correcta; la red no permite confirmar que exista')

    existe = _pagina_responde(url)
    if existe is False:
        return _resultado(DESCARTADO, 'La página no existe')
    if existe is None:
        return _resultado(SIN_VERIFICAR, 'No se pudo comprobar la página')
    return _resultado(VERIFICADO, 'La página responde')


# ------------------------------------------------- respaldo en las fuentes

def _solo_digitos(texto):
    return ''.join(ch for ch in texto if ch.isdigit())


def aparece_en_fuentes(valor, campo, texto_respaldado):
    """¿El dato aparece dentro del texto que Gemini marcó como respaldado por
    una búsqueda real? Si no aparece, es muy probable que lo haya completado
    él mismo."""
    if not texto_respaldado or not valor:
        return None  # no hay con qué comparar
    if campo in ('telefono', 'whatsapp'):
        digitos = _solo_digitos(valor)
        return len(digitos) >= 7 and digitos[-7:] in _solo_digitos(texto_respaldado)
    return valor.strip().lower() in texto_respaldado.lower()


# ----------------------------------------------------------- todo junto

CAMPOS_URL = ('sitio_web', 'linkedin_url', 'facebook_url', 'instagram_url')


def _bajar_a_dudoso(resultado, motivo):
    if resultado and resultado['estado'] == VERIFICADO:
        resultado['estado'] = DUDOSO
        resultado['motivo'] = motivo
    return resultado


def verificar_empresa(empresa, texto_respaldado='', usar_red=True):
    """Revisa todos los datos de contacto de una empresa. Devuelve una copia
    con los datos descartados vacíos y una clave 'verificacion' por campo."""
    empresa = dict(empresa)
    verificacion = {}
    descartados = {}

    pais = empresa.get('pais', '')
    for campo in ('telefono', 'whatsapp'):
        verificacion[campo] = verificar_telefono(empresa.get(campo, ''), pais)

    if usar_red:
        # El correo y el sitio web se revisan al mismo tiempo, no uno tras otro.
        with ThreadPoolExecutor(max_workers=2) as pool:
            f_email = pool.submit(verificar_email, empresa.get('email', ''), empresa.get('sitio_web', ''))
            f_web = pool.submit(verificar_url, empresa.get('sitio_web', ''), 'sitio_web')
            verificacion['email'] = f_email.result()
            verificacion['sitio_web'] = f_web.result()
        for campo in ('linkedin_url', 'facebook_url', 'instagram_url'):
            verificacion[campo] = verificar_url(empresa.get(campo, ''), campo)  # sin red, instantáneo
    else:
        if empresa.get('email'):
            ok = PATRON_EMAIL.match(empresa['email'].strip())
            verificacion['email'] = (_resultado(SIN_VERIFICAR, 'Revisión de red desactivada') if ok
                                     else _resultado(DESCARTADO, 'No tiene forma de correo'))
        for campo in CAMPOS_URL:
            if empresa.get(campo):
                verificacion[campo] = _resultado(SIN_VERIFICAR, 'Revisión de red desactivada')

    # Teléfonos y correos que no aparecen en ninguna fuente real: casi seguro inventados.
    for campo in ('telefono', 'whatsapp', 'email'):
        if aparece_en_fuentes(empresa.get(campo, ''), campo, texto_respaldado) is False:
            _bajar_a_dudoso(verificacion.get(campo), 'La IA no lo respaldó con ninguna página consultada')

    for campo, resultado in list(verificacion.items()):
        if resultado is None:
            del verificacion[campo]
            continue
        if resultado['estado'] == DESCARTADO:
            descartados[campo] = empresa.get(campo, '')
            empresa[campo] = ''
        elif resultado.get('normalizado'):
            empresa[campo] = resultado['normalizado']

    # WhatsApp: si la IA no trajo uno, un móvil válido se marca como "posible WhatsApp".
    tel = verificacion.get('telefono')
    empresa['whatsapp_posible'] = bool(
        not empresa.get('whatsapp') and tel and tel['estado'] != DESCARTADO and tel.get('es_movil')
    )

    empresa['verificacion'] = verificacion
    empresa['descartados'] = descartados
    return empresa


def verificar_empresas(empresas, texto_respaldado='', usar_red=True):
    """Verifica varias empresas en paralelo para no hacer esperar al operador."""
    if not empresas:
        return []
    with ThreadPoolExecutor(max_workers=min(5, len(empresas))) as pool:
        return list(pool.map(lambda e: verificar_empresa(e, texto_respaldado, usar_red), empresas))
