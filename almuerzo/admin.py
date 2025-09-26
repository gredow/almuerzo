from django.contrib import admin

from .forms import AlimentoPlatoInlineForm
from .models import (Alimento, AlimentoPlato, Carrera, Categoria, Estudiante,
                     Grado, Menu, MenuAlimento, MenuPlato, Nutriente,
                     NutrienteAlimento, Plato, Seccion, Servicio, Unidad)


class AlimentoPlatoInline(admin.TabularInline):
    model = AlimentoPlato
    extra = 1
    form = AlimentoPlatoInlineForm


class AlimentoInline(admin.TabularInline):
    model = Alimento
    extra = 0
    fields = ("nombre",)
    show_change_link = False


class MenuAlimentoInline(admin.TabularInline):
    model = MenuAlimento
    extra = 1


class MenuPlatoInline(admin.TabularInline):
    model = MenuPlato
    extra = 1


class NutrienteAlimentoInline(admin.TabularInline):
    model = NutrienteAlimento
    extra = 1


class SeccionInline(admin.TabularInline):
    model = Seccion
    extra = 0
    fields = ("nombre", "carrera")
    show_change_link = False


class EstudianteInline(admin.TabularInline):
    model = Estudiante
    extra = 0
    fields = ("nombre", "apellido","numero_orden")
    show_change_link = False


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
    inlines = [AlimentoInline]


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    search_fields = ["nombre"]

#EstudianteSeccion: arriba en un Inline


@admin.register(Grado)
class GradoAdmin(admin.ModelAdmin):
    search_fields = ["nombre"]
    inlines = [SeccionInline]



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
    search_fields = ("nombre",)
    inlines = [EstudianteInline]


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ("estudiante", "fecha_servido")
    list_filter = ("fecha_servido",)


@admin.register(Unidad)
class UnidadAdmin(admin.ModelAdmin):
    search_fields = ["nombre"]
