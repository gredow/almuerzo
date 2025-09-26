from django.db import models
from .unidad import Unidad


class Nutriente(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    unidad = models.ForeignKey(Unidad, on_delete=models.CASCADE)

    class Meta:
        ordering = ["id"]

    def __str__(self): return f"{self.nombre} ({self.unidad})"
