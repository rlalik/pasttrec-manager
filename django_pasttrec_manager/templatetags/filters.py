from django import template
from django.forms.boundfield import BoundField, BoundWidget
from django.forms import Select, NumberInput

register = template.Library()


@register.filter
def add_range(field, arg):
    a = arg.split(" ")
    return field.as_widget(
        attrs={
            "min": a[0],
            "max": a[1],
        }
    )
