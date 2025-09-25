from django.db import models


class Menu(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    descripcion = models.TextField(blank=True)
    fecha_creacion = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self): return self.nombre
