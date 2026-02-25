from django.contrib import admin

from .models import DespesaSecretaria, ReceitaResumo


@admin.register(ReceitaResumo)
class ReceitaResumoAdmin(admin.ModelAdmin):
    list_display = ("ano", "previsao", "arrecadacao")
    list_filter = ("ano",)


@admin.register(DespesaSecretaria)
class DespesaSecretariaAdmin(admin.ModelAdmin):
    list_display = ("ano", "secretaria", "orcamento", "empenhado", "liquidado", "pago")
    list_filter = ("ano", "secretaria")
    search_fields = ("secretaria",)
