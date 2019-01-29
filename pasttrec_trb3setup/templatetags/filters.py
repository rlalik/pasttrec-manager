from django import template
from django.forms.boundfield import BoundField, BoundWidget
from django.forms import Select, NumberInput

from ..views.cards import get_card_or_top_map

register = template.Library()

@register.filter(name='adddtclass')
def adddtclass(value, arg):
    a = arg.split(';')
    if len(a) > 0:
        value.field.widget.widgets[0].attrs = {'class': a[0]}
    if len(a) > 1:
        value.field.widget.widgets[1].attrs = {'class': a[1]}
    f = value.form
    return value

@register.filter(name='addclass')
def addclass(value, arg):
    if isinstance(value, BoundField):
        ## for select
        if isinstance(value.field.widget, Select):
          value.field.widget.attrs = {'class': arg}
        elif isinstance(value.field.widget, NumberInput):
          value.field.widget.attrs = {'class': arg}
    else:
        return value.as_widget(attrs = {'class': arg})

    return value

@register.filter(name='addrange')
def addrange(value, arg):
    a = arg.split(' ')
    return value.as_widget(attrs = {
        'min': a[0],
        'max': a[1],
        })

@register.filter(name='setcolortype')
def setcolortype(value):
    value.field.widget = ColorInput()
    return value


@register.filter(name='chbl')
def chbl(value):
    return '<span class="">{:d}</span>'.format(value)

@register.filter(name='chdis')
def chdis(value):
    if value is True:
        return '<span class="badge badge-danger">Y</span>'
    else:
        return '<span class="badge badge-success">N</span>'

@register.filter(name='lookup')
def lookup(value, arg):
    return value[arg]

@register.filter(name='top_map')
def top_map(value):
    return get_card_or_top_map(value)
