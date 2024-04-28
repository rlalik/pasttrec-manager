from django import template
from django.forms.boundfield import BoundField, BoundWidget
from django.forms import Select, NumberInput

register = template.Library()


@register.filter(name="add_class")
def addclass(value, arg):
    if isinstance(value, BoundField):
        ## for select
        if isinstance(value.field.widget, (Select, NumberInput)):
            value.field.widget.attrs = {"class": arg}
        else:
            value.field.widget.attrs = {"class": arg}
    else:
        # value.field.widget.attrs = {"class": arg}
        value.as_widget(attrs={"class": arg})
        # return value.as_widget(attrs={"class": arg})

    return value


@register.filter
def add_range(field, arg):
    a = arg.split(" ")
    return field.as_widget(
        attrs={
            "min": a[0],
            "max": a[1],
        }
    )
