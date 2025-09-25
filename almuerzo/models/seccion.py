from django.db import models
from .grado import Grado
from .carrera import Carrera


class Seccion(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    grado = models.ForeignKey(Grado, on_delete=models.CASCADE, related_name="grados")
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE, related_name="carreras")

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "Secciones"

    def __str__(self): return self.nombre
