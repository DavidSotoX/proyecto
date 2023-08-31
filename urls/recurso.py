from django.urls import path

from app.edificaciones.views import recurso

urlpatterns = [

    path('recurso/lista', recurso.RecursoLista.as_view(), name='recurso_lista'),
    path('recurso/crear', recurso.RecursoCrear.as_view(), name='recurso_crear'),
    path('recurso/editar/<int:pk>', recurso.RecursoEditar.as_view(), name='recurso_editar'),
    path('recurso/eliminar/<int:pk>', recurso.RecursoEliminar.as_view(), name='recurso_eliminar'),
    path('recurso/detalle/<int:pk>', recurso.RecursoDetalle.as_view(), name='recurso_detalle'),

    path('recursoitem/lista/<int:recurso_id>', recurso.RecursoItemLista.as_view(), name='recursoitem_lista'),
    path('recursoitem/crear/<int:recurso_id>', recurso.RecursoItemCrear.as_view(), name='recursoitem_crear'),
    path('recursoitem/editar/<int:pk>', recurso.RecursoitemEditar.as_view(), name='recursoitem_editar'),
    path('recursoitem/eliminar/<int:pk>', recurso.RecursoItemEliminar.as_view(), name='recursoitem_eliminar'),
]