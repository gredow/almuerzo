from django import forms
from .models import Alimento, Plato, AlimentoPlato, Servicio
from dal import autocomplete
from .models import AlimentoPlato, Categoria


class AlimentoForm(forms.ModelForm):
    class Meta:
        model = Alimento
        fields = ["nombre", "categoria"]


class AlimentoPlatoInlineForm(forms.ModelForm):
    class Meta:
        model = AlimentoPlato
        fields = ["alimento", "gramos"]


PlatoAlimentoFormSet = forms.inlineformset_factory(
    Plato, AlimentoPlato, form=AlimentoPlatoInlineForm, extra=1, can_delete=True
)


class FormPlato(forms.ModelForm):
    class Meta:
        model = Plato
        fields = ["nombre", "descripcion"]


class FormServicio(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ["estudiante", "estudiante"]

class FechaMenuForm(forms.Form):
    fecha = forms.DateField(
        label="Fecha del menú",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )


class NuevoServicioForm(forms.Form):
    estudiante_id = forms.IntegerField(
        label="ID del estudiante",
        min_value=1,
        widget=forms.NumberInput(attrs={"autofocus": "autofocus", "placeholder": "Ej. 123"})
    )


class AlimentoPlatoInlineForm(forms.ModelForm):
    # Campo auxiliar NO del modelo, solo para filtrar
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(),
        required=False,
        label="Filtrar por categoría"
    )

    class Meta:
        model = AlimentoPlato
        fields = ("categoria", "alimento", "gramos")  # incluir primero el filtro
        widgets = {
            "alimento": autocomplete.ModelSelect2(
                url="alimento-autocomplete",
                forward=["categoria"],
            )
        }