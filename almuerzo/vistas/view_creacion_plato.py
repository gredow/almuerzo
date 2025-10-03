from almuerzo.forms import FormPlato, PlatoAlimentoFormSet
from almuerzo.models import Plato
from django.shortcuts import render, redirect, get_object_or_404


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
