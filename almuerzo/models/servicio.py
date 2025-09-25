from django.db import models
from .menu import Menu
from .estudiante import Estudiante
from django.utils import timezone


class Servicio(models.Model):
    """
        Registro de los servicios tomados por cada estudiante en el día.
    """
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="servicios")
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name="servicios")
    notas = models.CharField(max_length=200, blank=True)
    fecha_servido = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["-estudiante"]
        unique_together = ("menu", "estudiante", "fecha_servido")

    def __str__(self):
        return f"{self.menu} - {self.estudiante}"
