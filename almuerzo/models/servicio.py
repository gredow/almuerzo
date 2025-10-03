from django.db import models
from .menu import Menu
from .estudiante import Estudiante
from django.utils import timezone


class Servicio(models.Model):
    """
        Registro de los servicios tomados por cada estudiante en el día.
    """
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name="servicios")
    fecha_servido = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_servido"]
        unique_together = ("estudiante", "fecha_servido")

    def __str__(self):
        return f"{self.estudiante} ({self.fecha_servido.strftime("%d-%m-%Y")})"
