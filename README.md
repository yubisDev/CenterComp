# ISYN CRM

CRM interno de **ISYN (Internacional de Subastas y Negocios)** para gestionar compradores, proveedores/consignantes e inventario, y conectar unos con otros.

Django 6 + plantillas del servidor + Bootstrap 5.3 (sin SPA). SQLite en local, PostgreSQL (Supabase) en producción, desplegado en Render.

## Funcionalidades

- **Compradores:** listado con filtros y tarjetas por estado, ficha con historial de contacto, importación CSV/Excel, importación por Hunter.io.
- **Proveedores / consignantes:** mismo esquema que compradores, para quienes le dan inventario a ISYN (incluye chatarreos).
- **Productos:** inventario con carga masiva CSV/Excel (duplicados detectados por `referencia`), ficha con compradores interesados y dashboard de KPIs.
- **Búsqueda con IA** (Gemini + Google Search) de compradores y de proveedores: hasta 5 empresas por búsqueda, corre en segundo plano y los resultados se revisan como borrador antes de guardarse.
- **Envío masivo de correo:** filtra por estado, país, sector y producto de interés, con plantilla y vista previa del mensaje.
- **Match automático:** al crear un producto, se avisa por correo a los compradores cuyas palabras clave de interés coincidan.
- Tema claro/oscuro y sidebar colapsable.

## Puesta en marcha local

Requiere Python 3.12+.

```bash
python -m venv venv
venv\Scripts\activate          # Windows  (Linux/macOS: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env         # Linux/macOS: cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abre `http://127.0.0.1:8000/`. No hay registro público: los usuarios se crean con `createsuperuser` o desde `/admin/`.

Tests:

```bash
python manage.py test prospeccion
```

## Variables de entorno

Se definen en `.env` (local) o en el panel de Render (producción). Ver `.env.example`.

| Variable | Descripción |
|---|---|
| `SECRET_KEY` | Clave secreta de Django. |
| `DEBUG` | `True` solo en local. |
| `ALLOWED_HOSTS` | Hosts permitidos, separados por coma. |
| `CSRF_TRUSTED_ORIGINS` | Necesaria al usar un dominio propio con HTTPS. |
| `DATABASE_URL` | URI de PostgreSQL. Sin ella se usa SQLite. |
| `GEMINI_API_KEY` | Habilita la búsqueda con IA. Sin ella la función aparece deshabilitada. |
| `BUSQUEDA_IA_LIMITE_DIARIO` | Tope de búsquedas con IA por día (por defecto 20). |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `DEFAULT_FROM_EMAIL` | Cuenta SMTP corporativa. |

> **Correo saliente:** el envío masivo y las alertas automáticas de match quedan **deshabilitados** hasta que `EMAIL_HOST`, `EMAIL_HOST_USER` y `EMAIL_HOST_PASSWORD` estén los tres configurados. Sin ellos, el sistema no simula envíos.

## Despliegue

Render toma el `render.yaml` del repositorio:

- **Build:** `pip install -r requirements.txt && python manage.py collectstatic --noinput`
- **Start:** `python manage.py migrate --noinput && gunicorn centercomp.wsgi --timeout 120`

Las migraciones se aplican solas en cada arranque. Basta con hacer push a `master`; las variables marcadas `sync: false` en `render.yaml` (`DATABASE_URL`, `GEMINI_API_KEY`, credenciales de correo) se cargan a mano en el panel de Render.

La base de datos está en Supabase; usar la cadena del **Session pooler** (puerto 5432). En el plan gratuito Supabase pausa el proyecto tras ~1 semana sin actividad, y mientras está pausado la app responde con error 500 hasta reanudarlo desde su panel.

## Estructura

```
centercomp/            configuración de Django (settings, urls, wsgi)
prospeccion/           app principal
  models.py            Comprador, Proveedor, Producto, plantillas, historial, BusquedaIA
  views.py             vistas de listados, fichas, importación, envío masivo y búsqueda con IA
  ia_busqueda.py       prompts y llamada a Gemini
  signals.py           match automático al crear productos
  templates/           plantillas de la app
templates/             base.html y login
static/                CSS (app.css) y JS
```

## Diseño

El sistema visual (tokens, tema oscuro, reglas de color) está documentado en [DESIGN.md](DESIGN.md), y el contexto de producto en [PRODUCT.md](PRODUCT.md).
