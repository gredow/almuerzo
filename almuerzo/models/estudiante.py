from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from .seccion import Seccion


class Estudiante(models.Model):
    SEXO_OPCIONES = [
        ("M", "Masculino"),
        ("F", "Femenino"),
    ]

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    lugar_de_residencia = models.CharField(max_length=100, default="AZUA")
    numero_orden = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(50)])
    sexo = models.CharField(max_length=1, choices=SEXO_OPCIONES,default="M")
    fecha_nacimiento = models.DateField(default="01-01-2010")
    # seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE, related_name="secciones")

    class Meta:
        ordering = ["apellido", "nombre"]

    def __str__(self): return f"{self.nombre} {self.apellido}"
