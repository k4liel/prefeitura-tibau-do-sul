from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from apps.monitoramento.models import Alerta


class Command(BaseCommand):
    help = "Cria perfis de acesso: publico, analista e admin."

    def handle(self, *args, **options):
        publico, _ = Group.objects.get_or_create(name="publico")
        analista, _ = Group.objects.get_or_create(name="analista")
        admin, _ = Group.objects.get_or_create(name="admin")

        perms_view = Permission.objects.filter(codename__startswith="view_")
        alerta_perms = Permission.objects.filter(
            content_type__app_label=Alerta._meta.app_label,
            codename__in=["add_alerta", "change_alerta"],
        )
        audit_view_perm = Permission.objects.filter(
            content_type__app_label=LogEntry._meta.app_label,
            codename="view_logentry",
        )

        analista.permissions.set(
            (perms_view | alerta_perms | audit_view_perm).distinct()
        )
        admin.permissions.set(Permission.objects.all())
        publico.permissions.clear()

        self.stdout.write(self.style.SUCCESS("Perfis de acesso criados/atualizados."))
