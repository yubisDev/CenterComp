from django.urls import path

from . import views

urlpatterns = [
    path('', views.compradores_lista, name='compradores_lista'),
    path('compradores/nuevo/', views.comprador_form, name='comprador_nuevo'),
    path('compradores/importar/', views.compradores_importar, name='compradores_importar'),
    path('compradores/buscar-ia/', views.compradores_buscar_ia, name='compradores_buscar_ia'),
    path('compradores/buscar-ia/ejecutar/', views.compradores_buscar_ia_ejecutar, name='compradores_buscar_ia_ejecutar'),
    path('compradores/buscar-ia/guardar/', views.compradores_buscar_ia_guardar, name='compradores_buscar_ia_guardar'),
    path('compradores/buscar-ia/descartar/', views.compradores_buscar_ia_descartar, name='compradores_buscar_ia_descartar'),
    path('compradores/<int:pk>/', views.comprador_detalle, name='comprador_detalle'),
    path('compradores/<int:pk>/editar/', views.comprador_form, name='comprador_editar'),
    path('compradores/<int:pk>/eliminar/', views.comprador_eliminar, name='comprador_eliminar'),
    path('compradores/<int:pk>/marcar-contactado/', views.comprador_marcar_contactado, name='comprador_marcar_contactado'),

    path('productos/', views.productos_lista, name='productos_lista'),
    path('productos/dashboard/', views.productos_dashboard, name='productos_dashboard'),
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
