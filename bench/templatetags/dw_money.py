"""Formatting-only template tags for bench (styleguide: tags format, never compute)."""

from django import template

register = template.Library()

_SYMBOLS = {"PHP": "₱", "USD": "$", "EUR": "€"}


@register.filter
def dw_symbol(currency_code: str) -> str:
    """Symbol for a stored currency code; unknown codes render as the code itself."""
    return _SYMBOLS.get(currency_code, f"{currency_code} ")
