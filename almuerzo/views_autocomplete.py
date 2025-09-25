from dal import autocomplete
from .models import Alimento

class AlimentoAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Alimento.objects.select_related("categoria").all()

        # Texto que escribe el usuario
        if self.q:
            qs = qs.filter(nombre__icontains=self.q)

        # Categoría enviada desde el inline (forward)
        categoria_id = self.forwarded.get("categoria", None)
        if categoria_id:
            qs = qs.filter(categoria_id=categoria_id)

        return qs
