from django.db import models
from django.utils import timezone


class Menu(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    fecha_creacion = models.DateField(default=timezone.now, unique= True)

    class Meta:
        ordering = ["-fecha_creacion"]

    def __str__(self): return f"{self.nombre} ({self.fecha_creacion})"
