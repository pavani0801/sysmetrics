from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name='divide')
def divide(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return None