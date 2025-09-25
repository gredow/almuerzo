from django.db import models


class AlimentoPlato(models.Model):
    plato = models.ForeignKey(
        'Plato',                # o 'almuerzo.Plato' si prefieres calificar con la app
        on_delete=models.CASCADE,
        related_name='alimentos_plato'
    )
    alimento = models.ForeignKey(
        'Alimento',          # o 'almuerzo.Alimento'
        on_delete=models.PROTECT,
        related_name='alimento_platos'
    )
    gramos = models.FloatField(help_text="Cantidad usada en la receta (gramos)")

    class Meta:
        unique_together = ("plato", "alimento")

    def __str__(self):
        return f"{self.plato} - {self.alimento} ({self.gramos} g)"
