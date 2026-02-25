from django.db import models


class ReceitaResumo(models.Model):
    ano = models.IntegerField(db_index=True)
    previsao = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    arrecadacao = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["ano"], name="uniq_receita_ano")]


class DespesaSecretaria(models.Model):
    ano = models.IntegerField(db_index=True)
    secretaria = models.CharField(max_length=255)
    orcamento = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    empenhado = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    liquidado = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    pago = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    class Meta:
        indexes = [models.Index(fields=["ano", "secretaria"])]
        constraints = [
            models.UniqueConstraint(
                fields=["ano", "secretaria"], name="uniq_despesa_ano_secretaria"
            )
        ]


class Emenda(models.Model):
    numero = models.CharField(max_length=50, blank=True)
    ano = models.IntegerField(db_index=True)
    autoria = models.CharField(max_length=255)
    tipo = models.CharField(max_length=120, blank=True)
    origem_recurso = models.CharField(max_length=120, blank=True)
    objeto = models.TextField(blank=True)
    funcao_governo = models.CharField(max_length=255, blank=True)
    beneficiario = models.CharField(max_length=255, blank=True)
    unidade = models.CharField(max_length=255, blank=True)
    valor_previsto = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    valor_empenhado = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    valor_liquidado = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    valor_pago = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    data_emenda = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-valor_previsto"]
        indexes = [models.Index(fields=["ano", "autoria"])]

    def __str__(self):
        return f"Emenda {self.numero} - {self.autoria}"


class OrcamentoItem(models.Model):
    ano = models.IntegerField(db_index=True)
    orgao_cod = models.CharField(max_length=20, blank=True)
    unidade = models.CharField(max_length=255)
    acao = models.CharField(max_length=255, blank=True)
    funcao = models.CharField(max_length=120, blank=True)
    subfuncao = models.CharField(max_length=120, blank=True)
    natureza_despesa = models.CharField(max_length=30, blank=True)
    elemento_despesa = models.CharField(max_length=255, blank=True)
    fonte_recurso = models.CharField(max_length=255, blank=True)
    valor_inicial = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    valor_atualizado = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    valor_disponivel = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    class Meta:
        ordering = ["-valor_inicial"]
        indexes = [models.Index(fields=["ano", "unidade"])]

    def __str__(self):
        return f"{self.unidade} - {self.acao}"
