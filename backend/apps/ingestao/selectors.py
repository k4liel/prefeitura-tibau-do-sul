from .models import SyncRun


def ultimas_execucoes(limite: int = 20):
    return SyncRun.objects.all()[:limite]
