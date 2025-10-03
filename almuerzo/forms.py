from django import forms
from .models import Alimento, Plato, AlimentoPlato, Servicio, Carrera, Seccion
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

# class FechaMenuForm(forms.Form):
#     fecha = forms.DateField(
#         label="Fecha del menú",
#         widget=forms.DateInput(attrs={"type": "date", "class": "form-control w-auto"})
#     )


class FechaMenuForm(forms.Form):
    fecha = forms.DateField(
        label="Fecha del menú",
        widget=forms.DateInput(attrs={'type': 'date'})
    )

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(
        label='Seleccionar archivo Excel',
        help_text='Formatos soportados: .xlsx, .xls',
        widget=forms.FileInput(attrs={'accept': '.xlsx,.xls'})
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


class FiltroServicioForm(forms.Form):
    fecha = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Fecha"
    )
    carrera = forms.ModelChoiceField(
        queryset=Carrera.objects.all(),
        required=True,
        label="Carrera",
        widget=forms.Select(attrs={'class': 'form-select'})

    )
    seccion = forms.ModelChoiceField(
        queryset=Seccion.objects.none(),
        required=True,
        label="Sección",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Si viene por GET (o POST), usar el id de carrera para filtrar secciones
        if 'carrera' in self.data:
            try:
                carrera_id = int(self.data.get('carrera'))
                self.fields['seccion'].queryset = Seccion.objects.filter(carrera_id=carrera_id).order_by('nombre')
            except (TypeError, ValueError):
                self.fields['seccion'].queryset = Seccion.objects.none()
        # Si hay initial (ej. al recargar con valores iniciales)
        elif self.initial.get('carrera'):
            self.fields['seccion'].queryset = Seccion.objects.filter(
                carrera=self.initial['carrera']
            ).order_by('nombre')

class FechaDashboardForm(forms.Form):
    fecha = forms.DateField(
        label="Fecha",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control w-auto"})
    )
    categoria_id = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control w-auto", "placeholder": "ID categoría"})
    )