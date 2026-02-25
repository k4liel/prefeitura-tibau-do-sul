from django.urls import path

from .views import (
    AlertasView,
    ContratosView,
    DashboardView,
    EmendasView,
    FinancasView,
    FontesAuditoriaView,
    FornecedoresView,
    FuncionariosView,
    GovernancaView,
    HierarquiaOrganizacionalView,
    LegislativoView,
    LicitacoesView,
    OrcamentoDetalhadoView,
    RemuneracoesView,
    SecretariasOrcamentoView,
    TecnologiaView,
)

app_name = "web"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("hierarquia/", HierarquiaOrganizacionalView.as_view(), name="hierarquia"),
    path("remuneracoes/", RemuneracoesView.as_view(), name="remuneracoes"),
    path("governanca/", GovernancaView.as_view(), name="governanca"),
    path("legislativo/", LegislativoView.as_view(), name="legislativo"),
    path("financas/", FinancasView.as_view(), name="financas"),
    path("secretarias/", SecretariasOrcamentoView.as_view(), name="secretarias"),
    path("funcionarios/", FuncionariosView.as_view(), name="funcionarios"),
    path("licitacoes/", LicitacoesView.as_view(), name="licitacoes"),
    path("contratos/", ContratosView.as_view(), name="contratos"),
    path("fornecedores/", FornecedoresView.as_view(), name="fornecedores"),
    path("tecnologia/", TecnologiaView.as_view(), name="tecnologia"),
    path("emendas/", EmendasView.as_view(), name="emendas"),
    path(
        "orcamento-detalhado/",
        OrcamentoDetalhadoView.as_view(),
        name="orcamento-detalhado",
    ),
    path("alertas/", AlertasView.as_view(), name="alertas"),
    path("fontes/", FontesAuditoriaView.as_view(), name="fontes"),
]
