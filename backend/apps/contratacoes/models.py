from django.db import models


class Licitacao(models.Model):
    certame = models.CharField(max_length=100, blank=True)
    modalidade = models.CharField(max_length=120, blank=True)
    objeto = models.TextField(blank=True)
    valor = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    ano = models.IntegerField(null=True, blank=True, db_index=True)
    data_publicacao = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=80, blank=True)
    tipo_objeto = models.CharField(max_length=120, blank=True)
    link_edital = models.URLField(max_length=500, blank=True)
    fonte = models.CharField(max_length=30, blank=True)

    class Meta:
        ordering = ["-valor"]


class Contrato(models.Model):
    numero = models.CharField(max_length=100, blank=True)
    empresa = models.CharField(max_length=255)
    modalidade = models.CharField(max_length=120, blank=True)
    objeto = models.TextField(blank=True)
    valor = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    cnpj = models.CharField(max_length=30, blank=True)
    ano = models.IntegerField(null=True, blank=True, db_index=True)
    data_inicio = models.DateField(null=True, blank=True)
    data_fim = models.DateField(null=True, blank=True)
    data_assinatura = models.DateField(null=True, blank=True)
    ativo = models.BooleanField(default=True)
    fonte = models.CharField(max_length=30, blank=True)

    class Meta:
        ordering = ["-valor"]
