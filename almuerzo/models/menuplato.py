from django.db import models
from .menu import Menu
from .plato import Plato


class MenuPlato(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    plato = models.ForeignKey(Plato, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("menu", "plato")
        ordering = ['id']

    def __str__(self): return f"{self.menu} {self.plato}"
