from django.db import models
from .menu import Menu
from .alimento import Alimento


class MenuAlimento(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    alimento = models.ForeignKey(Alimento, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("menu", "alimento")

    def __str__(self): return f"{self.menu} {self.alimento}"
