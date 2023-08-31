from django.urls import path

from app.edificaciones.views import campus

urlpatterns = [
    path('', campus.index, name='index'),

    path('campus/crear', campus.CampusCrear.as_view(), name='campus_crear'),
    path('campus/detalle/<int:pk>', campus.CampusDetalle.as_view(), name='campus_detalle'),
    path('campus/editar/<int:pk>', campus.CampusEditar.as_view(), name='campus_editar'),
    path('campus/eliminar/<int:pk>', campus.CampusEliminar.as_view(), name='campus_eliminar'),
    path('campus/lista', campus.CampusLista.as_view(), name='campus_lista'),
    path('campus/bloques/<int:campus_id>', campus.campus_bloques, name='campus_bloques'),

    path('bloque/crear/<int:campus_id>', campus.BloqueCrear.as_view(), name='bloque_crear'),
    path('bloque/editar/<int:pk>', campus.BloqueEditar.as_view(), name='bloque_editar'),
    path('bloque/eliminar/<int:pk>', campus.BloqueEliminar.as_view(), name='bloque_eliminar'),
    path('bloque/lista/<int:campus_id>', campus.BloqueLista.as_view(), name='bloque_lista'),
    path('bloque/pisos/<int:bloque_id>', campus.bloque_pisos, name='bloque_pisos'),
]
