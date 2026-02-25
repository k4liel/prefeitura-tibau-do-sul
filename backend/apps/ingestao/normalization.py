import re


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(value.strip().upper().split())


def normalize_cnpj(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\D", "", value)


def fornecedor_dedupe_key(nome: str | None, cnpj: str | None) -> str:
    cnpj_norm = normalize_cnpj(cnpj)
    if cnpj_norm:
        return f"cnpj:{cnpj_norm}"
    return f"nome:{normalize_text(nome)}"


def servidor_dedupe_key(
    nome: str | None, orgao: str | None, vinculo: str | None, matricula: str | None
) -> str:
    if matricula:
        return f"mat:{normalize_text(matricula)}"
    return "|".join(
        [
            normalize_text(nome),
            normalize_text(orgao),
            normalize_text(vinculo),
        ]
    )
