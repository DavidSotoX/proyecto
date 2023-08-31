from django.urls import include
from django.urls import path

app_name = 'edificaciones'

urlpatterns = [
    #CONFIGURACION
    path('', include('app.edificaciones.urls.campus')),
    path('', include('app.edificaciones.urls.catalogo')),
    path('', include('app.edificaciones.urls.recurso')),

    #EVALUACION
    path('', include('app.edificaciones.urls.ambiente')),
    path('', include('app.edificaciones.urls.reporte')),
]