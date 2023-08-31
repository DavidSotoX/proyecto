from django.urls import path

from app.edificaciones.views import ambiente

urlpatterns = [

    path('ambiente/crear', ambiente.AmbienteCrear.as_view(), name='ambiente_crear'),
    path('ambiente/editar/<int:pk>', ambiente.AmbienteEditar.as_view(), name='ambiente_editar'),
    path('ambiente/eliminar/<int:pk>', ambiente.AmbienteEliminar.as_view(), name='ambiente_eliminar'),
    path('ambiente/detalle/<int:pk>', ambiente.AmbienteDetalle.as_view(), name='ambiente_detalle'),
    path('ambiente/lista', ambiente.AmbienteLista.as_view(), name='ambiente_lista'),
    path('ambiente/años>', ambiente.obtener_anios_revisiones, name='ambiente_obtener_anios_revisiones'),
    
    path('ambiente-uso/crear/<int:ambiente_id>', ambiente.AmbienteUsoCrear.as_view(), name='ambiente_uso_crear'),
    path('ambiente-uso/editar/<int:pk>', ambiente.AmbienteUsoEditar.as_view(), name='ambiente_uso_editar'),
    path('ambiente-uso/eliminar/<int:pk>', ambiente.AmbienteUsoEliminar.as_view(), name='ambiente_uso_eliminar'),
    path('ambiente-uso/detalle/<int:pk>', ambiente.AmbienteUsoDetalle.as_view(), name='ambiente_uso_detalle'),
    path('ambiente-uso/lista/<int:ambiente_id>', ambiente.AmbienteUsoLista.as_view(), name='ambiente_uso_lista'),
    path('ambiente-uso/recursos/guardar/<int:ambiente_uso_id>/<int:recurso_id>', ambiente.ambiente_uso_recursos_guardar, name='ambiente_uso_recursos_guardar'),

    path('subambiente/crear/<int:ambiente_uso_id>', ambiente.SubambienteCrear.as_view(), name='subambiente_crear'),
    path('subambiente/editar/<int:pk>', ambiente.SubambienteEditar.as_view(), name='subambiente_editar'),
    path('subambiente/eliminar/<int:pk>', ambiente.SubambienteEliminar.as_view(), name='subambiente_eliminar'),

]