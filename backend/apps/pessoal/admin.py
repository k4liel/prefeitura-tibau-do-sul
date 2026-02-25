from django.contrib import admin

from .models import Servidor


@admin.register(Servidor)
class ServidorAdmin(admin.ModelAdmin):
    list_display = (
        "matricula",
        "nome",
        "orgao",
        "vinculo",
        "valor_bruto",
        "valor_liquido",
    )
    list_filter = ("orgao", "vinculo")
    search_fields = ("nome", "orgao", "vinculo")
