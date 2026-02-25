from django.db import models


class SyncRun(models.Model):
    fonte = models.CharField(max_length=120)
    status = models.CharField(max_length=30, default="pendente")
    iniciado_em = models.DateTimeField(auto_now_add=True)
    finalizado_em = models.DateTimeField(null=True, blank=True)
    mensagem = models.TextField(blank=True)
    erro_count = models.IntegerField(default=0)
    registro_count = models.IntegerField(default=0)

    class Meta:
        ordering = ["-iniciado_em"]


class DataProvenance(models.Model):
    fonte = models.CharField(max_length=120)
    endpoint = models.CharField(max_length=255)
    recurso = models.CharField(max_length=120)
    external_id = models.CharField(max_length=120, blank=True)
    payload_hash = models.CharField(max_length=64, unique=True)
    versao = models.CharField(max_length=30, default="v1")
    coletado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-coletado_em"]
        indexes = [models.Index(fields=["fonte", "recurso"])]
