from django.contrib import admin

from .forms import AlimentoPlatoInlineForm
from .models import (Alimento, AlimentoPlato, Carrera, Categoria, Estudiante,
                     EstudianteSeccion, Grado, Menu, MenuAlimento, MenuPlato, Nutriente,
                     NutrienteAlimento, Plato, Seccion, Servicio, Unidad)


class AlimentoPlatoInline(admin.TabularInline):
    model = AlimentoPlato
    extra = 1
    form = AlimentoPlatoInlineForm


class EstudianteSeccionInline(admin.TabularInline):
    model = EstudianteSeccion
    extra = 1


class MenuAlimentoInline(admin.TabularInline):
    model = MenuAlimento
    extra = 1


class MenuPlatoInline(admin.TabularInline):
    model = MenuPlato
    extra = 1


class NutrienteAlimentoInline(admin.TabularInline):
    model = NutrienteAlimento
    extra = 1


@admin.register(Alimento)
class AlimentoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria")
    list_filter = ("categoria",)
    search_fields = ("nombre", "categoria__nombre")
    inlines = [NutrienteAlimentoInline]

#AlimentoPlato más arriba Inline


@admin.register(Carrera)
class CarreraAdmin(admin.ModelAdmin):
    search_fields = ["nombre"]


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    search_fields = ["nombre"]


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    search_fields = ["nombre"]
    inlines = [EstudianteSeccionInline]

#EstudianteSeccion: arriba en un Inline


@admin.register(Grado)
class GradoAdmin(admin.ModelAdmin):
    search_fields = ["nombre"]


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    search_fields = ["nombre"]
    inlines = [MenuPlatoInline,MenuAlimentoInline]


@admin.register(Nutriente)
class NutrienteAdmin(admin.ModelAdmin):
    search_fields = ["nombre"]

#NutrienteAlimento más arriba Inline


@admin.register(Plato)
class PlatoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "fecha_creacion")
    search_fields = ("nombre",)
    inlines = [AlimentoPlatoInline]


@admin.register(Seccion)
class SeccionAdmin(admin.ModelAdmin):
    inlines = [EstudianteSeccionInline]


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ("menu", "estudiante", "notas")
    list_filter = ("fecha_servido", "menu")


@admin.register(Unidad)
class UnidadAdmin(admin.ModelAdmin):
    search_fields = ["nombre"]
