from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Q
from .models import (Alimento, AlimentoPlato, Categoria, Estudiante, Menu,
                     NutrienteAlimento, Plato, Servicio)
from .forms import AlimentoForm, FormPlato, PlatoAlimentoFormSet, FormServicio
from django.utils import timezone
from django.db import IntegrityError
from .forms import NuevoServicioForm


def inicio(request):
    return render(request, "almuerzo/inicio.html")


def lista_alimento(request):
    qs = Alimento.objects.select_related("categoria").all()
    return render(request, "almuerzo/lista_alimento.html", {"almuerzo": qs})


def lista_categoria(request):
    qs = Categoria.objects.all()
    return render(request, "almuerzo/lista_categoria.html", {"categorias": qs})


def creacion_alimento(request):
    form = AlimentoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("lista_alimento")
    return render(request, "almuerzo/form_alimento.html", {"form": form})


def cracion_plato(request):
    plato = Plato()
    if request.method == "POST":
        form = FormPlato(request.POST, instance=plato)
        formset = PlatoAlimentoFormSet(request.POST, instance=plato)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect("detalle_plato", pk=plato.pk)
    else:
        form = FormPlato(instance=plato)
        formset = PlatoAlimentoFormSet(instance=plato)
    return render(request, "almuerzo/form_plato.html", {"form": form, "formset": formset})


def detalle_plato(request, pk):
    plato = get_object_or_404(Plato, pk=pk)
    totals = plato.nutrientes_totales()
    di = AlimentoPlato.objects.filter(plato=plato).select_related("alimento")
    return render(request, "almuerzo/detalle_plato.html", {"plato": plato, "plato_alimentos": di, "totals": totals})


def creacion_servicio(request):
    form = FormServicio(request.POST or None)
    if request.method == "POST" and form.is_valid():
        serving = form.save()
        return redirect("plato_detalle", pk=serving.plato_id)
    return render(request, "almuerzo/form_servicio.html", {"form": form})


def estadisticas(request):
    """
    Ejemplo de estadística: ¿qué almuerzo aparecen en platos que
    suman más 'numero_persona' al ser servidos?
    """
    # Suma de personas por plato
    plato_persona = Servicio.objects.values("plato").annotate(total_people=Sum("numero_persona"))
    totales_por_plato = {row["plato"]: row["total_personas"] for row in plato_persona}

    # Agregar por alimento: suma de numero_persona de todos los platos donde aparece
    data = (AlimentoPlato.objects
            .select_related("alimento")
            .values("alimento_id", "alimento__nombre")
            .annotate(total_personas=Sum("plato__servicios__numero_persona"))
            .order_by("-total_personas"))

    return render(request, "almuerzo/estadisticas.html", {"alimento_rank": data})


def nuevo_servicio(request):
    """
    Flujo:
    - Recibe un ID de estudiante.
    - Verifica si existe el estudiante.
    - Verifica si existe un Menú para el día (fecha_creacion == hoy).
    - Si ambos existen, verifica si ya tiene Servicio para hoy y ese menú.
    - Crea el Servicio si no existe; muestra mensajes de estado en rojo/verde.
    """
    form = NuevoServicioForm(request.POST or None)
    msg = None
    msg_class = ""  # "error" (rojo) o "success" (verde)

    if request.method == "POST" and form.is_valid():
        est_id = form.cleaned_data["estudiante_id"]
        hoy = timezone.localdate()

        # 1) Estudiante
        try:
            estudiante = Estudiante.objects.get(pk=est_id)
        except Estudiante.DoesNotExist:
            msg = f"No existe un estudiante con ID {est_id}."
            msg_class = "error"
            return render(request, "almuerzo/nuevo_servicio.html", {"form": form, "msg": msg, "msg_class": msg_class})

        # 2) Menú del día
        menu = Menu.objects.filter(fecha_creacion=hoy).order_by("-id").first()
        if not menu:
            msg = f"No se ha establecido un menú para el día {hoy}."
            msg_class = "error"
            return render(request, "almuerzo/nuevo_servicio.html", {"form": form, "msg": msg, "msg_class": msg_class})

        # 3) ¿Ya tomó el servicio hoy?
        ya_tomo = Servicio.objects.filter(menu=menu, estudiante=estudiante, fecha_servido=hoy).exists()
        if ya_tomo:
            msg = f"{estudiante} ya tomó el servicio del menú de hoy ({menu.nombre})."
            msg_class = "error"
        else:
            try:
                Servicio.objects.create(menu=menu, estudiante=estudiante)
                msg = f"Servicio agregado para {estudiante} en el menú de hoy ({menu.nombre})."
                msg_class = "success"
                form = NuevoServicioForm()  # limpia el campo
            except IntegrityError:
                # Respaldo por si la unicidad salta al mismo tiempo
                msg = f"{estudiante} ya tomó el servicio del menú de hoy ({menu.nombre})."
                msg_class = "error"

    return render(request, "almuerzo/nuevo_servicio.html", {"form": form, "msg": msg, "msg_class": msg_class})
