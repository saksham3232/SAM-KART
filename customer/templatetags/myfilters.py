from django import template
from django.forms.boundfield import BoundField

register = template.Library()

@register.filter(name='addclass')
def addclass(value, css_class):
    if isinstance(value, BoundField):
        value.field.widget.attrs['class'] = css_class
    return value

@register.filter(name='addplaceholder')
def addplaceholder(value, placeholder):
    if isinstance(value, BoundField):
        value.field.widget.attrs['placeholder'] = placeholder
    return value

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''
