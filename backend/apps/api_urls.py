from django.urls import include, path

urlpatterns = [
    path("dashboard/", include("apps.dashboard_api")),
    path("governanca/", include("apps.governanca.api")),
    path("legislativo/", include("apps.legislativo.api")),
    path("pessoal/", include("apps.pessoal.api")),
    path("financas/", include("apps.financas.api")),
    path("contratacoes/", include("apps.contratacoes.api")),
    path("fornecedores/", include("apps.fornecedores.api")),
    path("monitoramento/", include("apps.monitoramento.api")),
    path("ingestao/", include("apps.ingestao.api")),
]
