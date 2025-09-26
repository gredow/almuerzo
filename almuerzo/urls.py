from django.contrib import admin
from django.shortcuts import render
from django.urls import path

from . import views
from .views import tabla_platos
from .views_autocomplete import AlimentoAutocomplete

urlpatterns = [
    path("", views.inicio, name="home"),
    path("alimentos/", views.lista_alimento, name="lista_alimento"),
    path("categorias/", views.lista_categoria, name="lista_categoria"),
    path("almuerzo/nuevo/", views.creacion_alimento, name="creacion_alimento"),
    path("platos/nuevo/", views.cracion_plato, name="cracion_plato"),
    path("platos/<int:pk>/", views.detalle_plato, name="detalle_plato"),
    path("estadisticas/", views.estadisticas, name="estadisticas"),
    path('admin/', admin.site.urls),
    path("autocomplete/alimento/", AlimentoAutocomplete.as_view(), name="alimento-autocomplete"),
    path("servicios/nuevo/", views.nuevo_servicio, name="nuevo_servicio"),
    path('platos/tabla/', tabla_platos, name='tabla_platos'),
    path("menu/porfecha/", views.menu_por_fecha, name="menu_por_fecha"),
]
