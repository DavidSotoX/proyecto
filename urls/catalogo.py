from django.urls import path

from app.edificaciones.views import catalogo

urlpatterns = [

    path('catalogo/lista', catalogo.CatalogoLista.as_view(), name='catalogo_lista'),
    path('catalogo/crear', catalogo.CatalogoCrear.as_view(), name='catalogo_crear'),
    path('catalogo/editar/<int:pk>', catalogo.CatalogoEditar.as_view(), name='catalogo_editar'),
    path('catalogo/eliminar/<int:pk>', catalogo.CatalogoEliminar.as_view(), name='catalogo_eliminar'),
    path('catalogo/detalle/<int:pk>', catalogo.CatalogoDetalle.as_view(), name='catalogo_detalle'),

    path('catalogoitem/lista/<int:catalogo_id>', catalogo.CatalogoItemLista.as_view(), name='catalogoitem_lista'),
    path('catalogoitem/crear/<int:catalogo_id>', catalogo.CatalogoitemCrear.as_view(), name='catalogoitem_crear'),
    path('catalogoitem/editar/<int:pk>', catalogo.CatalogoitemEditar.as_view(), name='catalogoitem_editar'),
    path('catalogoitem/eliminar/<int:pk>', catalogo.CatalogoitemEliminar.as_view(), name='catalogoitem_eliminar'),
]