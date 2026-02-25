from django.db import models


class Servidor(models.Model):
    matricula = models.CharField(max_length=80, blank=True, db_index=True)
    nome = models.CharField(max_length=255)
    orgao = models.CharField(max_length=255)
    vinculo = models.CharField(max_length=80, blank=True)
    valor_bruto = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    valor_liquido = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    cargo = models.CharField(max_length=255, blank=True)
    funcao = models.CharField(max_length=255, blank=True)
    carga_horaria = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ["nome"]
        indexes = [models.Index(fields=["orgao", "vinculo"])]

    def __str__(self) -> str:
        return self.nome
