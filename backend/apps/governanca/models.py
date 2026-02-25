from django.db import models


class Secretaria(models.Model):
    nome = models.CharField(max_length=255, unique=True)
    gestor = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self) -> str:
        return self.nome
