from django.contrib import admin
from django.shortcuts import render
from django.urls import path

from . import views
from . import vistas
from .views import tabla_platos
from .views_autocomplete import AlimentoAutocomplete

urlpatterns = [
    # path("", views.inicio, name="home"),
    path("", views.home_almuerzo, name="home_almuerzo"),
    path("alimentos/", views.lista_alimento, name="lista_alimento"),
    path("categorias/", views.lista_categoria, name="lista_categoria"),
    path("almuerzo/nuevo/", views.creacion_alimento, name="creacion_alimento"),
    path("platos/nuevo/", vistas.cracion_plato, name="cracion_plato"),
    path("platos/<int:pk>/", views.detalle_plato, name="detalle_plato"),
    path("estadisticas/", views.estadisticas, name="estadisticas"),
    path('admin/', admin.site.urls),
    path("autocomplete/alimento/", AlimentoAutocomplete.as_view(), name="alimento-autocomplete"),
    path("servicios/nuevo/", views.nuevo_servicio, name="nuevo_servicio"),
    path('platos/tabla/', tabla_platos, name='tabla_platos'),
    path("menu/porfecha/", views.menu_por_fecha, name="menu_por_fecha"),
    path('upload-excel/', vistas.upload_excel, name='upload_excel'),
    path("filtro-servicio/", views.filtro_servicio_view, name="filtro_servicio"),
    path("alimentos/porcentaje/", views.alimentos_porcentaje_view, name="alimentos_porcentaje"),
    path("api/alimentos/porcentaje/", views.api_alimentos_porcentaje, name="api_alimentos_porcentaje"),
]