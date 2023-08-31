from django.urls import path

from app.edificaciones.views import reporte

urlpatterns = [
    path('ambiente/xls/detallado', reporte.ambiente_xls_detallado, name='ambiente_xls_detallado'),
]