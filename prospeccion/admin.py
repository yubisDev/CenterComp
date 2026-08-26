from django.contrib import admin

from .models import Comprador, HistorialContacto, PlantillaMensaje, Producto


class HistorialContactoInline(admin.TabularInline):
    model = HistorialContacto
    extra = 0
    readonly_fields = ['fecha']


@admin.register(Comprador)
class CompradorAdmin(admin.ModelAdmin):
    list_display = ['nombre_empresa', 'pais', 'ciudad', 'sector', 'estado', 'fuente', 'fecha_ultimo_contacto']
    list_filter = ['estado', 'pais', 'sector', 'fuente']
    search_fields = ['nombre_empresa', 'pais', 'sector', 'email', 'telefono']
    filter_horizontal = ['productos_interes']
    inlines = [HistorialContactoInline]


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'cantidad_disponible', 'precio_referencia']
    list_filter = ['categoria']
    search_fields = ['nombre', 'categoria']


@admin.register(HistorialContacto)
class HistorialContactoAdmin(admin.ModelAdmin):
    list_display = ['comprador', 'medio', 'fecha', 'usuario']
    list_filter = ['medio']


@admin.register(PlantillaMensaje)
class PlantillaMensajeAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo']
    list_filter = ['tipo']
