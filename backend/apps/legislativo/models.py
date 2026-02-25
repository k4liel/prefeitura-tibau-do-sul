from django.db import models


class Vereador(models.Model):
    nome = models.CharField(max_length=255)
    partido = models.CharField(max_length=60)
    mandato = models.CharField(max_length=20, default="2025-2028")

    class Meta:
        ordering = ["nome"]
        constraints = [
            models.UniqueConstraint(
                fields=["nome", "mandato"], name="uniq_vereador_nome_mandato"
            )
        ]

    def __str__(self) -> str:
        return self.nome
