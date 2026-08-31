"""
Búsqueda de compradores potenciales con IA (Gemini + Google Search).

Reglas duras de este módulo, por diseño:
- La IA SIEMPRE busca en la web real (grounding); nunca se le pide que
  "invente" o "adivine" un dato. Si no encuentra algo, debe dejarlo vacío.
- Los resultados nunca se guardan directo como Comprador — el llamador
  (la vista) los muestra como borrador para que el usuario revise y
  apruebe antes de que entren al CRM real.
- Cada búsqueda queda registrada (BusquedaIA) para poder aplicar un tope
  diario y así nunca acercarse a un gasto inesperado.
"""
import json
import re

from django.conf import settings

PROMPT_PLANTILLA = """\
Eres un asistente de investigación B2B para un exportador colombiano que \
busca compradores potenciales para sus productos.

Usa la búsqueda de Google para encontrar hasta {maximo} EMPRESAS REALES que \
coincidan con esta descripción: "{consulta}"

Reglas estrictas:
- Solo incluye empresas que existan de verdad y que hayas podido confirmar \
con la búsqueda. Nunca inventes ni "completes" un dato que no encontraste.
- Si no encuentras el correo, teléfono o sitio web de una empresa, deja ese \
campo como cadena vacía "" — NO lo adivines ni generes uno con formato \
plausible.
- No repitas empresas.

Responde ÚNICAMENTE con un array JSON (sin texto antes ni después, sin \
bloque de código markdown) con este formato exacto:

[
  {{
    "nombre_empresa": "...",
    "pais": "...",
    "ciudad": "...",
    "sector": "...",
    "email": "...",
    "telefono": "...",
    "sitio_web": "...",
    "resumen": "Una frase breve de por qué encaja o qué hace la empresa"
  }}
]
"""


class BusquedaIAError(Exception):
    pass


def _extraer_json(texto):
    texto = texto.strip()
    texto = re.sub(r'^```(?:json)?\s*', '', texto)
    texto = re.sub(r'\s*```$', '', texto)
    inicio = texto.find('[')
    fin = texto.rfind(']')
    if inicio == -1 or fin == -1 or fin < inicio:
        raise BusquedaIAError('La IA no devolvió un formato reconocible.')
    fragmento = texto[inicio:fin + 1]
    try:
        return json.loads(fragmento)
    except json.JSONDecodeError as exc:
        raise BusquedaIAError(f'No se pudo interpretar la respuesta de la IA: {exc}') from exc


def buscar_empresas(consulta, maximo=8):
    """Devuelve (lista_de_empresas, lista_de_fuentes). Lanza BusquedaIAError
    con un mensaje entendible si algo falla (sin API key, sin crédito, la
    IA no devolvió JSON válido, etc.)."""
    if not settings.GEMINI_API_KEY:
        raise BusquedaIAError(
            'La búsqueda con IA no está configurada (falta GEMINI_API_KEY).'
        )

    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        raise BusquedaIAError('Falta instalar la librería google-genai.') from exc

    try:
        # Límite de tiempo explícito: sin esto, una llamada que se cuelga
        # puede reintentar varias veces por debajo antes de fallar — cada
        # reintento es una llamada real y cobrable, y como el intento nunca
        # "termina bien", ni siquiera queda registrado en BusquedaIA para
        # el tope diario. Un timeout corto acota el daño de cualquier
        # incidente a un solo intento fallido.
        http_options = types.HttpOptions(timeout=45_000)  # ms
        client = genai.Client(api_key=settings.GEMINI_API_KEY, http_options=http_options)
        grounding_tool = types.Tool(google_search=types.GoogleSearch())
        config = types.GenerateContentConfig(tools=[grounding_tool])
        response = client.models.generate_content(
            model='gemini-3.7-flash',
            contents=PROMPT_PLANTILLA.format(consulta=consulta.strip(), maximo=maximo),
            config=config,
        )
    except Exception as exc:  # noqa: BLE001 — cualquier falla de red/API debe verse como mensaje amigable
        raise BusquedaIAError(f'La IA no respondió correctamente: {exc}') from exc

    if not response.text:
        raise BusquedaIAError('La IA no devolvió ningún resultado.')

    empresas_crudas = _extraer_json(response.text)
    empresas = []
    for item in empresas_crudas:
        if not isinstance(item, dict) or not item.get('nombre_empresa'):
            continue
        empresas.append({
            'nombre_empresa': str(item.get('nombre_empresa', ''))[:200],
            'pais': str(item.get('pais', ''))[:100],
            'ciudad': str(item.get('ciudad', ''))[:100],
            'sector': str(item.get('sector', ''))[:120],
            'email': str(item.get('email', ''))[:254],
            'telefono': str(item.get('telefono', ''))[:30],
            'sitio_web': str(item.get('sitio_web', ''))[:200],
            'resumen': str(item.get('resumen', ''))[:300],
        })

    fuentes = []
    try:
        metadata = response.candidates[0].grounding_metadata
        if metadata and metadata.grounding_chunks:
            for chunk in metadata.grounding_chunks:
                if chunk.web:
                    fuentes.append({'titulo': chunk.web.title, 'url': chunk.web.uri})
    except (AttributeError, IndexError, TypeError):
        pass

    return empresas, fuentes
