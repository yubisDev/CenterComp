from django.urls import path

from . import views

urlpatterns = [
    path('', views.compradores_lista, name='compradores_lista'),
    path('compradores/nuevo/', views.comprador_form, name='comprador_nuevo'),
    path('compradores/importar/', views.compradores_importar, name='compradores_importar'),
    path('compradores/buscar-ia/', views.compradores_buscar_ia, name='compradores_buscar_ia'),
    path('compradores/buscar-ia/ejecutar/', views.compradores_buscar_ia_ejecutar, name='compradores_buscar_ia_ejecutar'),
    path('compradores/buscar-ia/estado/<int:busqueda_id>/', views.compradores_buscar_ia_estado, name='compradores_buscar_ia_estado'),
    path('compradores/buscar-ia/guardar/', views.compradores_buscar_ia_guardar, name='compradores_buscar_ia_guardar'),
    path('compradores/buscar-ia/descartar/', views.compradores_buscar_ia_descartar, name='compradores_buscar_ia_descartar'),
    path('compradores/<int:pk>/', views.comprador_detalle, name='comprador_detalle'),
    path('compradores/<int:pk>/editar/', views.comprador_form, name='comprador_editar'),
    path('compradores/<int:pk>/eliminar/', views.comprador_eliminar, name='comprador_eliminar'),
    path('compradores/<int:pk>/marcar-contactado/', views.comprador_marcar_contactado, name='comprador_marcar_contactado'),

    path('proveedores/', views.proveedores_lista, name='proveedores_lista'),
    path('proveedores/nuevo/', views.proveedor_form, name='proveedor_nuevo'),
    path('proveedores/buscar-ia/', views.proveedores_buscar_ia, name='proveedores_buscar_ia'),
    path('proveedores/buscar-ia/ejecutar/', views.proveedores_buscar_ia_ejecutar, name='proveedores_buscar_ia_ejecutar'),
    path('proveedores/buscar-ia/estado/<int:busqueda_id>/', views.proveedores_buscar_ia_estado, name='proveedores_buscar_ia_estado'),
    path('proveedores/buscar-ia/guardar/', views.proveedores_buscar_ia_guardar, name='proveedores_buscar_ia_guardar'),
    path('proveedores/buscar-ia/descartar/', views.proveedores_buscar_ia_descartar, name='proveedores_buscar_ia_descartar'),
    path('proveedores/<int:pk>/', views.proveedor_detalle, name='proveedor_detalle'),
    path('proveedores/<int:pk>/editar/', views.proveedor_form, name='proveedor_editar'),
    path('proveedores/<int:pk>/eliminar/', views.proveedor_eliminar, name='proveedor_eliminar'),
    path('proveedores/<int:pk>/marcar-contactado/', views.proveedor_marcar_contactado, name='proveedor_marcar_contactado'),

    path('productos/', views.productos_lista, name='productos_lista'),
    path('productos/dashboard/', views.productos_dashboard, name='productos_dashboard'),
    path('productos/importar/', views.productos_importar, name='productos_importar'),
    path('productos/nuevo/', views.producto_form, name='producto_nuevo'),
    path('productos/<int:pk>/', views.producto_detalle, name='producto_detalle'),
    path('productos/<int:pk>/editar/', views.producto_form, name='producto_editar'),
    path('productos/<int:pk>/eliminar/', views.producto_eliminar, name='producto_eliminar'),

    path('compradores/envio-masivo/', views.compradores_envio_masivo, name='compradores_envio_masivo'),
    path('compradores/envio-masivo/enviar/', views.compradores_envio_masivo_enviar, name='compradores_envio_masivo_enviar'),

    path('plantillas/', views.plantillas_lista, name='plantillas_lista'),
    path('plantillas/nueva/', views.plantilla_form, name='plantilla_nueva'),
    path('plantillas/<int:pk>/editar/', views.plantilla_form, name='plantilla_editar'),
    path('plantillas/<int:pk>/eliminar/', views.plantilla_eliminar, name='plantilla_eliminar'),

    path('api/importar/hunter/', views.api_importar_hunter, name='api_importar_hunter'),
]
