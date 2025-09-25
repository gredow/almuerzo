from django.db import models
from .alimento import Alimento
from .nutriente import Nutriente


class NutrienteAlimento(models.Model):
    """
    Valor por 100 g del alimento.
    """
    alimento = models.ForeignKey(Alimento, on_delete=models.CASCADE)
    nutriente = models.ForeignKey(Nutriente, on_delete=models.CASCADE)
    valor_por_100g = models.FloatField()  # ejemplo: 13.5 (g de proteína por 100 g)

    class Meta:
        unique_together = ("alimento", "nutriente")

    def __str__(self):
        return f"{self.alimento} - {self.nutriente}: {self.valor_por_100g} /100g"
