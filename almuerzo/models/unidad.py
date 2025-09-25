from django.db import models


class Unidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    abreviatura = models.CharField(max_length=4, unique=True)
    equivalencia_gramos = models.FloatField(help_text="Cantidad a la que equivale en gramos la unidad")

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "Unidades"

    def __str__(self): return self.nombre
