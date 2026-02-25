from django.contrib import admin

from .models import Vereador


@admin.register(Vereador)
class VereadorAdmin(admin.ModelAdmin):
    list_display = ("nome", "partido", "mandato")
    list_filter = ("partido", "mandato")
    search_fields = ("nome", "partido")
