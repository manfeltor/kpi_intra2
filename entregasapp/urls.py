from django.urls import path
from .views import render_main_despacho_vs_entrega

urlpatterns = [
    path('', render_main_despacho_vs_entrega, name="despacho_vs_entregas_main"),
]