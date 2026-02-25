from django.contrib import admin

from .models import Contrato, Licitacao


@admin.register(Licitacao)
class LicitacaoAdmin(admin.ModelAdmin):
    list_display = ("certame", "modalidade", "valor")
    list_filter = ("modalidade",)
    search_fields = ("certame", "objeto")


@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ("numero", "empresa", "modalidade", "valor")
    list_filter = ("modalidade",)
    search_fields = ("numero", "empresa", "objeto")
