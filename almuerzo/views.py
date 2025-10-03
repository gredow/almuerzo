from collections import defaultdict

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Q
from .models import (Alimento, AlimentoPlato, Categoria, Estudiante, Menu,
                     NutrienteAlimento, Plato, Servicio)
from .forms import AlimentoForm, FormPlato, PlatoAlimentoFormSet, FormServicio, FechaMenuForm, FiltroServicioForm, \
    FechaDashboardForm
from django.utils import timezone
from django.db import IntegrityError
from .forms import NuevoServicioForm
from django.db.models import Prefetch


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


# def cracion_plato(request):
#     plato = Plato()
#     if request.method == "POST":
#         form = FormPlato(request.POST, instance=plato)
#         formset = PlatoAlimentoFormSet(request.POST, instance=plato)
#         if form.is_valid() and formset.is_valid():
#             form.save()
#             formset.save()
#             return redirect("detalle_plato", pk=plato.pk)
#     else:
#         form = FormPlato(instance=plato)
#         formset = PlatoAlimentoFormSet(instance=plato)
#     return render(request, "almuerzo/form_plato.html", {"form": form, "formset": formset})


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
        ya_tomo = False
        # ya_tomo = Servicio.objects.filter(menu=menu, estudiante=estudiante, fecha_servido=hoy).exists()
        if ya_tomo:
            msg = f"{estudiante} ya tomó el servicio del menú de hoy."
            msg_class = "error"
        else:
            try:
                Servicio.objects.create(estudiante=estudiante)
                msg = f"Servicio agregado para {estudiante} en el menú de hoy."
                msg_class = "success"
                form = NuevoServicioForm()  # limpia el campo
            except IntegrityError:
                # Respaldo por si la unicidad salta al mismo tiempo
                msg = f"{estudiante} ya tomó el servicio del menú de hoy."
                msg_class = "error"

    return render(request, "almuerzo/nuevo_servicio.html", {"form": form, "msg": msg, "msg_class": msg_class})


def tabla_platos(request):
    platos = (
        Plato.objects
        .prefetch_related(
            Prefetch(
                'alimentos_plato',
                queryset=AlimentoPlato.objects.select_related('alimento').order_by('alimento__nombre')
            )
        )
        .order_by('nombre')
    )
    # Preparamos una lista (plato, items) para facilitar el rowspan en el template
    data = [(p, list(p.alimentos_plato.all())) for p in platos]
    return render(request, 'almuerzo/platos_tabla.html', {'data': data})


def menu_por_fecha(request):
    """
    Selecciona una fecha; carga el menú con fecha_creacion == fecha.
    Renderiza:
      - Nombre y descripción del menú
      - Platos -> Alimentos (gramos) -> Nutrientes (valor escalado)
      - Totales por nutriente del menú completo
    """
    form = FechaMenuForm(request.GET or None)

    menu = None
    platos_render = []         # [{plato: Plato, items: [{alimento, gramos, nutrientes: [{nutriente, valor}]}]}]
    nutrientes_totales = None  # [{id, nombre, total, unidad}]

    if form.is_valid():
        fecha = form.cleaned_data["fecha"]

        # Busca el menú por fecha (ajusta si usas otro campo/criterio):
        menu = (Menu.objects
                    .filter(fecha_creacion=fecha)
                    .first())

        if menu:
            cantidad_estudiantes = Servicio.objects.filter(
                fecha_servido=fecha
            ).values("estudiante").distinct().count()
            # Traemos todas las filas AlimentoPlato de los platos del menú
            qs_alimentos_plato = (AlimentoPlato.objects
                .filter(plato__menuplato__menu=menu)
                .select_related("plato", "alimento")
                .prefetch_related("alimento__nutrientealimento_set__nutriente")
            )

            # Armamos estructura por plato
            platos_dict = {}  # plato_id -> {'plato': obj, 'items': [...]}
            for ap in qs_alimentos_plato:
                entry = platos_dict.setdefault(ap.plato_id, {"plato": ap.plato, "items": []})

                # Nutrientes del alimento escalados por gramos usados en la receta
                nutrientes_escalados = []
                for na in ap.alimento.nutrientealimento_set.all():
                    valor_escalado = (na.valor_por_100g * ap.gramos) / 100.0
                    nutrientes_escalados.append({
                        "nutriente": na.nutriente,   # se usará .nombre y .unidad en la template
                        "valor": valor_escalado,
                    })

                entry["items"].append({
                    "alimento": ap.alimento,
                    "gramos": ap.gramos,
                    "nutrientes": nutrientes_escalados,
                })

            platos_render = list(platos_dict.values())

            # Totales por nutriente en TODO el menú
            totales = defaultdict(float)
            nombres = {}
            unidades = {}

            for bloque in platos_render:
                for item in bloque["items"]:
                    for nut in item["nutrientes"]:
                        n = nut["nutriente"]
                        nid = n.id
                        totales[nid] += nut["valor"]
                        nombres[nid] = getattr(n, "nombre", f"Nutriente {nid}")
                        unidades[nid] = getattr(n, "unidad", "")

            orden_ids = [1, 2, 3, 4,5,8,9,10]

        nutrientes_totales = [
            {"id": nid, "nombre": nombres[nid], "total": total, "unidad": unidades[nid]}
            for nid, total in totales.items()
        ]

        # crear un diccionario {id: índice} para acceso rápido
        mapa_orden = {nid: i for i, nid in enumerate(orden_ids)}

        # usar .get con un valor grande para ids no incluidos en la lista
        nutrientes_totales.sort(key=lambda x: mapa_orden.get(x["id"], float("inf")))

    ctx = {
        "form": form,
        "menu": menu,
        "platos": platos_render,
        "nutrientes_totales": nutrientes_totales,
    }
    return render(request, "almuerzo/menu_por_fecha.html", ctx)


def filtro_servicio_view(request):
    estudiantes = None
    form = FiltroServicioForm(request.GET or None)

    # Si el usuario ya seleccionó valores válidos, ejecutar búsqueda
    if form.is_valid():
        fecha = form.cleaned_data.get("fecha")
        seccion = form.cleaned_data.get("seccion")
        if fecha and seccion:
            estudiantes = Estudiante.objects.filter(
                servicios__fecha_servido=fecha,
                seccion=seccion
            ).distinct().order_by('apellido', 'nombre')

    return render(request, "almuerzo/filtro_servicio.html", {
        "form": form,
        "estudiantes": estudiantes
    })



from collections import defaultdict
from statistics import mean

from django.db.models import Prefetch, Count
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from .models import (
    Alimento, AlimentoPlato, Categoria, Estudiante, Menu, MenuPlato, Servicio
)


def alimentos_porcentaje_view(request):
    """
    Página con el gráfico y el filtro por categoría.
    """
    categorias = Categoria.objects.order_by("nombre").all()
    return render(request, "almuerzo/alimentos_porcentaje.html", {"categorias": categorias})


def api_alimentos_porcentaje(request):
    """
    API JSON:
    Calcula, para cada alimento, el PROMEDIO del porcentaje de estudiantes que lo comieron.
    Lógica:
      - Tomamos cada fecha con 'Servicio' (hubo servicio ese día).
      - Emparejamos con el 'Menu' de esa fecha (Menu.fecha_creacion == fecha_servido).
      - Por cada alimento que aparece en los platos de ese menú, asumimos que
        los estudiantes que recibieron el servicio ese día son los que "comieron" ese alimento.
      - Porcentaje fecha = (#estudiantes con servicio ese día) / (total_estudiantes) * 100
      - Para cada alimento: promedio de todos sus porcentajes a través de las fechas en que apareció.

    Filtro opcional:
      - ?categoria_id=<id>  (o ?categoria=<nombre>)
    """
    categoria_id = request.GET.get("categoria_id")
    categoria_nombre = request.GET.get("categoria")

    total_estudiantes = Estudiante.objects.count() or 1  # evitar división por cero

    # 1) Fechas en las que hubo servicio y cuántos estudiantes recibieron servicio en cada fecha
    servicios_qs = (
        Servicio.objects
        .values("fecha_servido")
        .annotate(cantidad=Count("estudiante", distinct=True))
        .order_by("fecha_servido")
    )
    if not servicios_qs:
        return JsonResponse({"labels": [], "data": []})

    # Mapa: fecha -> cantidad de servicios (estudiantes distintos)
    servicios_por_fecha = {row["fecha_servido"]: row["cantidad"] for row in servicios_qs}
    fechas_servicio = list(servicios_por_fecha.keys())

    # 2) Menús para esas fechas, con prefetch hasta Alimento (y su Categoria)
    menus = (
        Menu.objects
        .filter(fecha_creacion__in=fechas_servicio)
        .prefetch_related(
            Prefetch(
                "menuplato_set",
                queryset=MenuPlato.objects.select_related("plato").prefetch_related(
                    Prefetch(
                        "plato__alimentos_plato",
                        queryset=AlimentoPlato.objects.select_related("alimento__categoria")
                    )
                ),
            )
        )
    )

    # 3) Opcional: filtrar por categoría (para evitar cargar/computar innecesario)
    categoria_obj = None
    if categoria_id:
        try:
            categoria_obj = Categoria.objects.get(pk=categoria_id)
        except Categoria.DoesNotExist:
            categoria_obj = None
    elif categoria_nombre:
        try:
            categoria_obj = Categoria.objects.get(nombre=categoria_nombre)
        except Categoria.DoesNotExist:
            categoria_obj = None

    # 4) Agregar porcentajes por alimento
    porcentajes_por_alimento = defaultdict(list)  # alimento_id -> [porc_fecha, ...]
    nombre_alimento = {}
    categoria_alimento = {}

    for menu in menus:
        fecha = menu.fecha_creacion
        if fecha not in servicios_por_fecha:
            continue

        # porcentaje de ese día (respecto al total de estudiantes)
        porc_dia = (servicios_por_fecha[fecha] / total_estudiantes) * 100.0

        # Recolectar alimentos únicos del menú de ese día
        alimentos_del_menu = set()
        for mp in menu.menuplato_set.all():
            for ap in mp.plato.alimentos_plato.all():
                a = ap.alimento
                # Filtro por categoría si vino en la query
                if categoria_obj and a.categoria_id != categoria_obj.id:
                    continue
                alimentos_del_menu.add(a)

        # Asignar el porcentaje del día a cada alimento servido ese día
        for a in alimentos_del_menu:
            porcentajes_por_alimento[a.id].append(porc_dia)
            nombre_alimento[a.id] = a.nombre
            categoria_alimento[a.id] = a.categoria.nombre if a.categoria_id else ""

    # 5) Calcular promedio por alimento
    resultado = []
    for aid, lst in porcentajes_por_alimento.items():
        if not lst:
            continue
        resultado.append({
            "alimento_id": aid,
            "alimento": nombre_alimento.get(aid, f"Alimento {aid}"),
            "categoria": categoria_alimento.get(aid, ""),
            "porcentaje_promedio": round(mean(lst), 2),
            "muestras": len(lst),  # cuántas fechas contribuyeron
        })

    # Orden sugerido: desc por porcentaje
    resultado.sort(key=lambda x: x["porcentaje_promedio"], reverse=True)

    # Respuesta para Chart.js
    labels = [r["alimento"] for r in resultado]
    data = [r["porcentaje_promedio"] for r in resultado]

    return JsonResponse({
        "labels": labels,
        "data": data,
        "meta": {
            "total_estudiantes": total_estudiantes,
            "fechas_consideradas": len(fechas_servicio),
            "categoria": (categoria_obj.nombre if categoria_obj else "Todas"),
        }
    })


def home_almuerzo(request):
    """
    Dashboard de inicio:
    - Hero + imagen
    - Selector de fecha (default: hoy)
    - KPIs: estudiantes, servicios del día, alimentos, platos
    - Menú del día (platos -> alimentos)
    - Gráfico interactivo (alimentos por % promedio de estudiantes)
    """
    # fecha por defecto = hoy (zona servidor)
    default_fecha = timezone.localdate()
    form = FechaDashboardForm(request.GET or None, initial={"fecha": default_fecha})

    if form.is_valid():
        fecha = form.cleaned_data["fecha"]
        categoria_id = form.cleaned_data.get("categoria_id")
    else:
        fecha = default_fecha
        categoria_id = None

    # KPIs
    total_estudiantes = Estudiante.objects.count()
    servicios_dia = Servicio.objects.filter(fecha_servido=fecha).values("estudiante").distinct().count()
    total_alimentos = Alimento.objects.count()
    total_platos = Plato.objects.count()

    # Menú del día
    menu = (
        Menu.objects
        .filter(fecha_creacion=fecha)
        .prefetch_related(
            Prefetch(
                "menuplato_set",
                queryset=MenuPlato.objects.select_related("plato").prefetch_related(
                    Prefetch(
                        "plato__alimentos_plato",
                        queryset=AlimentoPlato.objects.select_related("alimento__categoria")
                    )
                ),
            )
        )
        .first()
    )

    # Estructura amigable para template: platos → alimentos
    platos_render = []
    if menu:
        for mp in menu.menuplato_set.all():
            items = []
            for ap in mp.plato.alimentos_plato.all():
                items.append({
                    "alimento": ap.alimento,
                    "categoria": ap.alimento.categoria.nombre if ap.alimento.categoria_id else "",
                    "gramos": ap.gramos,
                })
            platos_render.append({
                "plato": mp.plato,
                "items": items
            })

    # Categorías para el filtro del gráfico
    categorias = Categoria.objects.order_by("nombre").all()

    ctx = {
        "form": form,
        "fecha": fecha,
        "menu": menu,
        "platos": platos_render,
        "kpis": {
            "total_estudiantes": total_estudiantes,
            "servicios_dia": servicios_dia,
            "total_alimentos": total_alimentos,
            "total_platos": total_platos,
        },
        "categorias": categorias,
        "categoria_id": categoria_id or "",
    }
    return render(request, "almuerzo/home.html", ctx)


