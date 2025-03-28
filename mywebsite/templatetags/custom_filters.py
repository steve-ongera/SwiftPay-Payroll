from django import template
from calendar import month_name

register = template.Library()

@register.filter
def month_name_filter(month_number):
    """Convert month number (1-12) to full month name."""
    try:
        return month_name[month_number]
    except (IndexError, KeyError):
        return str(month_number)  # Fallback to number if invalid