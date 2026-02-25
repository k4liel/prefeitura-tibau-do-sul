from django.db import models


class Fornecedor(models.Model):
    nome = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=30, blank=True)
    valor_total = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    class Meta:
        ordering = ["-valor_total"]
        indexes = [models.Index(fields=["nome"]), models.Index(fields=["cnpj"])]

    def __str__(self) -> str:
        return self.nome
