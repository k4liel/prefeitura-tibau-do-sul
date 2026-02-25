from decimal import Decimal

from django import template

register = template.Library()


def _to_decimal(value):
    if value is None:
        return Decimal("0")
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


@register.filter
def currency_brl(value):
    amount = _to_decimal(value)
    formatted = f"{amount:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {formatted}"


@register.filter
def percent(value):
    amount = _to_decimal(value)
    formatted = f"{amount:.1f}".replace(".", ",")
    return f"{formatted}%"
