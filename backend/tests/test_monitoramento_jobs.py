import pytest
from django.core.management import call_command

from apps.ingestao.models import SyncRun
from apps.monitoramento.models import Alerta

pytestmark = pytest.mark.django_db


def test_monitor_sync_health_creates_alert_for_failure_rate():
    SyncRun.objects.create(fonte="job-a", status="erro")
    SyncRun.objects.create(fonte="job-a", status="erro")
    SyncRun.objects.create(fonte="job-a", status="sucesso")

    call_command("monitor_sync_health", max_failure_rate=10)

    assert Alerta.objects.filter(codigo="job-failure-job-a").exists()
