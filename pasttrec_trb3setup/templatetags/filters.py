from django import template
from django.forms.boundfield import BoundField, BoundWidget

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
    return value.as_widget(attrs = {'class': arg})

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
