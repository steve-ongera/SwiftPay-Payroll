# In your_app/templatetags/month_tags.py
from django import template
from calendar import month_name

register = template.Library()

@register.filter
def month_name_filter(month_number):
    """Convert month number (1-12) to month name"""
    try:
        return month_name[month_number]
    except (IndexError, KeyError):
        return str(month_number)

@register.filter
def months_range(count):
    """Return range of months (1-count)"""
    return range(1, count+1)