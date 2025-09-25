from django.db import models
from .alimento import Alimento
from .alimentoplato import AlimentoPlato


class Plato(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    descripcion = models.TextField(blank=True)
    alimentos = models.ManyToManyField(Alimento, through="AlimentoPlato", related_name="platos")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self): return self.nombre

    def nutrientes_totales(self):
        """
        Devuelve dict { nutriente_id: {"nombre": str, "unidad": str, "total": float} }
        Σ(valor_por_100g * gramos / 100) para cada nutriente del plato.
        """

        # Traemos filas de la intermedia (AlimentoPlato) y unimos con NutrienteAlimento
        rows = (
            AlimentoPlato.objects
            .filter(plato=self)
            .values(
                "gramos",
                "alimento_id",
                "alimento__nombre",
                "alimento__nutrientes__nutriente_id",
                "alimento__nutrientes__nutriente__nombre",
                "alimento__nutrientes__nutriente__unidad",
                "alimento__nutrientes__valor_por_100g",
            )
        )

        totales = {}
        for r in rows:
            nid = r["alimento__nutrientes__nutriente_id"]
            if nid is None:
                # El alimento puede no tener cargado ese nutriente aún
                continue
            nombre = r["alimento__nutrientes__nutriente__nombre"]
            unidad = r["alimento__nutrientes__nutriente__unidad"]
            gramos = r["gramos"] or 0.0
            val100 = r["alimento__nutrientes__valor_por_100g"] or 0.0
            aporte = val100 * gramos / 100.0

            if nid not in totales:
                totales[nid] = {"nombre": nombre, "unidad": unidad, "total": 0.0}
            totales[nid]["total"] += aporte

        return totales

    # def nutrientes_totales(self):
    #     """
    #     Devuelve un diccionario: { nutriente_id: {"nombre":..., "unidad":..., "total": float} }
    #     Calculado a partir de PlatoAlimento.gramos e NutrienteAlimento.valor_por_100g.
    #     """
    #     # Traer (nutriente, valor_per_100g, gramos)
    #     q = NutrienteAlimento.objects.filter(
    #         alimento__platoalimento__plato=self
    #     ).values(
    #         "nutriente_id", "nutriente__nombre", "nutriente__unidad",
    #         "alimento_id", "alimento__nombre",
    #         "alimento__alimentoplato__gramos",
    #         "valor_por_100g",
    #     )
    #
    #     totales = {}
    #     for row in q:
    #         grams = row["alimento__alimentoplato__gramos"] or 0.0
    #         val = (row["valor_por_100g"] or 0.0) * grams / 100.0
    #         nid = row["nutriente_id"]
    #         if nid not in totales:
    #             totales[nid] = {
    #                 "nombre": row["nutriente__nombre"],
    #                 "unidad": row["nutriente__unidad"],
    #                 "total": 0.0,
    #             }
    #         totales[nid]["total"] += val
    #     return totales