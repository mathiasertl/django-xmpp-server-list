from django import template
from django.forms.fields import DateField

register = template.Library()

@register.filter
def fieldvalue(field):
    if hasattr(field.field, 'choices'):
        for k, v in field.field.choices:
            if k == field.value():
                return v
        return 'key not found'
    elif type(field.field) == DateField:
        val = field.value()
        if val.__class__ == unicode:
            return val
        return field.value().strftime('%Y-%m-%d')
    else:
        return field.value()