from django.contrib import admin

from .models import Alerta


@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "titulo", "severidade", "criado_em")
    list_filter = ("severidade",)
    search_fields = ("codigo", "titulo", "detalhes")
