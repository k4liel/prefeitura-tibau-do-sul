from django.db import models


class Alerta(models.Model):
    codigo = models.CharField(max_length=80)
    titulo = models.CharField(max_length=255)
    severidade = models.CharField(max_length=20, default="media")
    detalhes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
