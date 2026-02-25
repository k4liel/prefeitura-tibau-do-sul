from django.contrib import admin

from .models import DataProvenance, SyncRun


@admin.register(SyncRun)
class SyncRunAdmin(admin.ModelAdmin):
    list_display = (
        "fonte",
        "status",
        "iniciado_em",
        "finalizado_em",
        "registro_count",
        "erro_count",
    )
    list_filter = ("fonte", "status")
    search_fields = ("fonte", "mensagem")


@admin.register(DataProvenance)
class DataProvenanceAdmin(admin.ModelAdmin):
    list_display = ("fonte", "recurso", "external_id", "versao", "coletado_em")
    list_filter = ("fonte", "recurso", "versao")
    search_fields = ("endpoint", "external_id", "payload_hash")
