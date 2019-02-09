from django import template
from django.template.loader import get_template

register = template.Library()


@register.filter
def bootstrap(form):
    template = get_template("bootstrapform/form.html")
    return template.render({'form': form})


@register.simple_tag
def bootstrap_field(field):
    return field.as_widget(attrs={'class': 'form-control'})


@register.inclusion_tag('bootstrapform/submit.html')
def bootstrap_submit(label):
    return {'label': label}


@register.filter
def is_checkbox(field):
    return field.field.widget.__class__.__name__.lower() == "checkboxinput"
