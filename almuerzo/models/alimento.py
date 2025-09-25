from django.db import models
from .categoria import Categoria


class Alimento(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="alimento")

    class Meta:
        ordering = ["nombre"]

    def __str__(self): return self.nombre
