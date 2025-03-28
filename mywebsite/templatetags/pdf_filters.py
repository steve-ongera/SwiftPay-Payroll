from django import template

register = template.Library()

@register.filter
def intcomma(value):
    """Format numbers with commas (1000 → 1,000)"""
    if value is None:
        return ""
    return "{:,.2f}".format(float(value))