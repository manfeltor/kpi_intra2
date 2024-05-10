from django.urls import path
from .views import base, construccion

urlpatterns = [
    path('', base, name="home"),
    path('enconstruccion/', construccion, name="construccion")
]
