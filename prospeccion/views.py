import csv
import io
from urllib.parse import quote

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import (
    CompradorForm,
    HistorialContactoForm,
    ImportarCompradoresForm,
    PlantillaMensajeForm,
    ProductoForm,
)
from .models import Comprador, HistorialContacto, PlantillaMensaje, Producto

FUENTE_ALIASES = {
    'hunter': Comprador.Fuente.HUNTER,
    'hunter.io': Comprador.Fuente.HUNTER,
    'apollo': Comprador.Fuente.APOLLO,
    'procolombia': Comprador.Fuente.PROCOLOMBIA,
    'camara de comercio': Comprador.Fuente.CAMARA_COMERCIO,
    'cámara de comercio': Comprador.Fuente.CAMARA_COMERCIO,
    'linkedin': Comprador.Fuente.LINKEDIN,
    'linkedin sales navigator': Comprador.Fuente.LINKEDIN,
    'manual': Comprador.Fuente.MANUAL,
}


def _construir_mensaje(comprador):
    """Devuelve (asunto_email, cuerpo_email, cuerpo_whatsapp) usando la primera
    plantilla disponible de cada tipo, o un mensaje genérico si no hay ninguna."""
    producto = comprador.productos_interes.first()
    producto_nombre = producto.nombre if producto else ''

    plantilla_email = PlantillaMensaje.objects.filter(tipo=PlantillaMensaje.Tipo.EMAIL).first()
    if plantilla_email:
        asunto, cuerpo_email = plantilla_email.render(comprador, producto_nombre)
    else:
        asunto = f'Oferta de producto para {comprador.nombre_empresa}'
        cuerpo_email = (
            f'Hola,\n\nNos gustaría ofrecerles nuestros productos disponibles en bodega'
            + (f' ({producto_nombre})' if producto_nombre else '')
            + '.\n\nQuedamos atentos.\n'
        )

    plantilla_wa = PlantillaMensaje.objects.filter(tipo=PlantillaMensaje.Tipo.WHATSAPP).first()
    if plantilla_wa:
        _, cuerpo_whatsapp = plantilla_wa.render(comprador, producto_nombre)
    else:
        cuerpo_whatsapp = (
            f'Hola {comprador.nombre_empresa}, les escribimos para ofrecerles nuestros productos'
            + (f' ({producto_nombre})' if producto_nombre else '')
            + '. ¿Les interesaría recibir más información?'
        )

    return asunto, cuerpo_email, cuerpo_whatsapp


def _enriquecer(comprador):
    asunto, cuerpo_email, cuerpo_whatsapp = _construir_mensaje(comprador)
    comprador.mailto_url = f'mailto:{comprador.email}?subject={quote(asunto)}&body={quote(cuerpo_email)}'
    numero = comprador.whatsapp_numero
    comprador.whatsapp_url = f'https://wa.me/{numero}?text={quote(cuerpo_whatsapp)}' if numero else ''
    return comprador


@login_required
def compradores_lista(request):
    qs = Comprador.objects.select_related().prefetch_related('productos_interes')

    q = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '')
    pais = request.GET.get('pais', '')
    sector = request.GET.get('sector', '')
    fuente = request.GET.get('fuente', '')

    if q:
        qs = qs.filter(
            Q(nombre_empresa__icontains=q) | Q(pais__icontains=q) | Q(sector__icontains=q)
        )
    if estado:
        qs = qs.filter(estado=estado)
    if pais:
        qs = qs.filter(pais=pais)
    if sector:
        qs = qs.filter(sector=sector)
    if fuente:
        qs = qs.filter(fuente=fuente)

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    for comprador in page_obj.object_list:
        _enriquecer(comprador)

    paises = Comprador.objects.exclude(pais='').values_list('pais', flat=True).distinct().order_by('pais')
    sectores = Comprador.objects.exclude(sector='').values_list('sector', flat=True).distinct().order_by('sector')

    querystring = request.GET.copy()
    querystring.pop('page', None)

    context = {
        'page_obj': page_obj,
        'estados': Comprador.Estado.choices,
        'fuentes': Comprador.Fuente.choices,
        'paises': paises,
        'sectores': sectores,
        'filtros': {'q': q, 'estado': estado, 'pais': pais, 'sector': sector, 'fuente': fuente},
        'querystring': querystring.urlencode(),
    }
    return render(request, 'prospeccion/compradores_lista.html', context)


@login_required
def comprador_detalle(request, pk):
    comprador = get_object_or_404(Comprador, pk=pk)
    _enriquecer(comprador)

    if request.method == 'POST':
        form = HistorialContactoForm(request.POST)
        if form.is_valid():
            historial = form.save(commit=False)
            historial.comprador = comprador
            historial.usuario = request.user
            historial.save()
            comprador.fecha_ultimo_contacto = timezone.now()
            if comprador.estado == Comprador.Estado.POR_CONTACTAR:
                comprador.estado = Comprador.Estado.CONTACTADO
            comprador.save()
            messages.success(request, 'Contacto registrado en el historial.')
            return redirect('comprador_detalle', pk=comprador.pk)
    else:
        form = HistorialContactoForm()

    context = {
        'comprador': comprador,
        'historial': comprador.historial.select_related('usuario'),
        'form': form,
    }
    return render(request, 'prospeccion/comprador_detalle.html', context)


@login_required
def comprador_form(request, pk=None):
    comprador = get_object_or_404(Comprador, pk=pk) if pk else None
    if request.method == 'POST':
        form = CompradorForm(request.POST, instance=comprador)
        if form.is_valid():
            form.save()
            messages.success(request, 'Comprador guardado correctamente.')
            return redirect('compradores_lista')
    else:
        form = CompradorForm(instance=comprador)
    return render(request, 'prospeccion/comprador_form.html', {'form': form, 'comprador': comprador})


@login_required
@require_POST
def comprador_eliminar(request, pk):
    comprador = get_object_or_404(Comprador, pk=pk)
    comprador.delete()
    messages.success(request, 'Comprador eliminado.')
    return redirect('compradores_lista')


@login_required
@require_POST
def comprador_marcar_contactado(request, pk):
    comprador = get_object_or_404(Comprador, pk=pk)
    comprador.fecha_ultimo_contacto = timezone.now()
    if comprador.estado == Comprador.Estado.POR_CONTACTAR:
        comprador.estado = Comprador.Estado.CONTACTADO
    comprador.save()
    HistorialContacto.objects.create(
        comprador=comprador,
        medio=request.POST.get('medio', HistorialContacto.Medio.OTRO),
        resultado='Marcado como contactado desde el listado.',
        usuario=request.user,
    )
    messages.success(request, f'{comprador.nombre_empresa} marcado como contactado.')
    next_url = request.POST.get('next') or reverse('compradores_lista')
    return redirect(next_url)


@login_required
def compradores_importar(request):
    resumen = None
    if request.method == 'POST':
        form = ImportarCompradoresForm(request.POST, request.FILES)
        if form.is_valid():
            resumen = _procesar_importacion(form.cleaned_data['archivo'])
            if resumen['errores']:
                messages.warning(request, f"Importación completada con {len(resumen['errores'])} error(es).")
            else:
                messages.success(request, f"Se importaron {resumen['creados']} compradores nuevos.")
    else:
        form = ImportarCompradoresForm()
    return render(request, 'prospeccion/compradores_importar.html', {'form': form, 'resumen': resumen})


def _procesar_importacion(archivo):
    nombre = archivo.name.lower()
    filas = []
    errores = []

    if nombre.endswith('.csv'):
        contenido = archivo.read().decode('utf-8-sig', errors='replace')
        lector = csv.DictReader(io.StringIO(contenido))
        for fila in lector:
            filas.append({(k or '').strip().lower(): (v or '').strip() for k, v in fila.items()})
    elif nombre.endswith('.xlsx') or nombre.endswith('.xls'):
        import openpyxl

        wb = openpyxl.load_workbook(archivo, read_only=True, data_only=True)
        ws = wb.active
        filas_iter = ws.iter_rows(values_only=True)
        encabezados = [str(h).strip().lower() if h else '' for h in next(filas_iter)]
        for fila in filas_iter:
            valores = {}
            for header, valor in zip(encabezados, fila):
                if header:
                    valores[header] = str(valor).strip() if valor is not None else ''
            if any(valores.values()):
                filas.append(valores)
    else:
        return {'creados': 0, 'errores': ['Formato de archivo no soportado. Usa CSV o Excel (.xlsx).']}

    creados = 0
    for i, fila in enumerate(filas, start=2):
        nombre_empresa = fila.get('nombre_empresa') or fila.get('empresa') or ''
        if not nombre_empresa:
            errores.append(f'Fila {i}: falta nombre_empresa, se omitió.')
            continue

        fuente_raw = (fila.get('fuente') or '').strip().lower()
        fuente = FUENTE_ALIASES.get(fuente_raw, Comprador.Fuente.MANUAL)

        email = fila.get('email') or fila.get('correo') or ''
        existente = None
        if email:
            existente = Comprador.objects.filter(nombre_empresa__iexact=nombre_empresa, email__iexact=email).first()
        if existente:
            errores.append(f'Fila {i}: "{nombre_empresa}" ya existe, se omitió.')
            continue

        Comprador.objects.create(
            nombre_empresa=nombre_empresa,
            pais=fila.get('pais') or fila.get('país') or '',
            ciudad=fila.get('ciudad') or '',
            sector=fila.get('sector') or fila.get('industria') or '',
            email=email,
            telefono=fila.get('telefono') or fila.get('teléfono') or fila.get('whatsapp') or '',
            fuente=fuente,
        )
        creados += 1

    return {'creados': creados, 'errores': errores}


# --- Productos ---

@login_required
def productos_lista(request):
    productos = Producto.objects.all()
    q = request.GET.get('q', '').strip()
    if q:
        productos = productos.filter(Q(nombre__icontains=q) | Q(categoria__icontains=q))
    return render(request, 'prospeccion/productos_lista.html', {'productos': productos, 'q': q})


@login_required
def producto_form(request, pk=None):
    producto = get_object_or_404(Producto, pk=pk) if pk else None
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto guardado correctamente.')
            return redirect('productos_lista')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'prospeccion/producto_form.html', {'form': form, 'producto': producto})


@login_required
@require_POST
def producto_eliminar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    producto.delete()
    messages.success(request, 'Producto eliminado.')
    return redirect('productos_lista')


# --- Plantillas ---

@login_required
def plantillas_lista(request):
    plantillas = PlantillaMensaje.objects.all()
    return render(request, 'prospeccion/plantillas_lista.html', {'plantillas': plantillas})


@login_required
def plantilla_form(request, pk=None):
    plantilla = get_object_or_404(PlantillaMensaje, pk=pk) if pk else None
    if request.method == 'POST':
        form = PlantillaMensajeForm(request.POST, instance=plantilla)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plantilla guardada correctamente.')
            return redirect('plantillas_lista')
    else:
        form = PlantillaMensajeForm(instance=plantilla)
    return render(request, 'prospeccion/plantilla_form.html', {'form': form, 'plantilla': plantilla})


@login_required
@require_POST
def plantilla_eliminar(request, pk):
    plantilla = get_object_or_404(PlantillaMensaje, pk=pk)
    plantilla.delete()
    messages.success(request, 'Plantilla eliminada.')
    return redirect('plantillas_lista')


# --- Integración externa (preparado para futuro, ej. Hunter.io) ---

@login_required
@require_POST
def api_importar_hunter(request):
    """
    Endpoint preparado para integrar una API externa de prospección
    (ej. Hunter.io Domain Search) y guardar los resultados como nuevos
    Compradores con fuente=hunter.

    Aún no implementado: requiere configurar HUNTER_API_KEY en el entorno
    y añadir la llamada real a la API dentro de esta vista. Por ahora
    devuelve 501 para dejar el contrato de la ruta ya definido.

    Uso esperado (cuando esté implementado):
      POST /api/importar/hunter/  {"dominio": "empresa.com", "sector": "textil"}
      -> crea Compradores con fuente=Comprador.Fuente.HUNTER y devuelve
         {"creados": N, "compradores": [...]}
    """
    return JsonResponse(
        {'detail': 'Integración con Hunter.io aún no configurada.'},
        status=501,
    )
