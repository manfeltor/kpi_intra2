from django.urls import path
from .views import render_main_despacho_vs_entrega


urlpatterns = [
    path('entregas/',render_main_despacho_vs_entrega, name='entregas_gerencia'),
]
