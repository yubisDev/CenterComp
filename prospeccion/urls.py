from django.urls import path

from . import views

urlpatterns = [
    path('', views.compradores_lista, name='compradores_lista'),
    path('compradores/nuevo/', views.comprador_form, name='comprador_nuevo'),
    path('compradores/importar/', views.compradores_importar, name='compradores_importar'),
    path('compradores/<int:pk>/', views.comprador_detalle, name='comprador_detalle'),
    path('compradores/<int:pk>/editar/', views.comprador_form, name='comprador_editar'),
    path('compradores/<int:pk>/eliminar/', views.comprador_eliminar, name='comprador_eliminar'),
    path('compradores/<int:pk>/marcar-contactado/', views.comprador_marcar_contactado, name='comprador_marcar_contactado'),

    path('productos/', views.productos_lista, name='productos_lista'),
    path('productos/nuevo/', views.producto_form, name='producto_nuevo'),
    path('productos/<int:pk>/editar/', views.producto_form, name='producto_editar'),
    path('productos/<int:pk>/eliminar/', views.producto_eliminar, name='producto_eliminar'),

    path('plantillas/', views.plantillas_lista, name='plantillas_lista'),
    path('plantillas/nueva/', views.plantilla_form, name='plantilla_nueva'),
    path('plantillas/<int:pk>/editar/', views.plantilla_form, name='plantilla_editar'),
    path('plantillas/<int:pk>/eliminar/', views.plantilla_eliminar, name='plantilla_eliminar'),

    path('api/importar/hunter/', views.api_importar_hunter, name='api_importar_hunter'),
]
