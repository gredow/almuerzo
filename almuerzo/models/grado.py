from django.db import models


class Grado(models.Model):
    nombre = models.CharField(max_length=10, unique=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self): return self.nombre
