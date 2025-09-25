from django.db import models
from .estudiante import Estudiante
from .seccion import Seccion


class EstudianteSeccion(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name="estudiantes")
    seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE, related_name="secciones")

    class Meta:
        unique_together = (("estudiante", "seccion"),)

    def __str__(self): return f"{self.seccion} - {self.estudiante}"
