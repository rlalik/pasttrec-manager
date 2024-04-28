from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django import forms

import re

HEXA_STR = "^(0[xX])?([A-Fa-f0-9]{1,16})$"
HEXA_RE = re.compile(HEXA_STR)
HEXA_VALID = RegexValidator(HEXA_RE, _("Enter a valid hex number "), "invalid")


def parse_hex(hex_string):
    HEXA_VALID(hex_string)

    return re.match(HEXA_RE, hex_string).group(2)


class HexFormField(forms.CharField):
    default_error_messages = {
        "invalid": 'Enter a valid hexfigure: e.g. "ff0022"',
    }

    def clean(self, value):
        print("clean", value)
        if not (value == "" and not self.required) and not re.match(HEXA_STR, value):
            raise forms.ValidationError(self.error_messages["invalid"])
        return value

    def clean_febid(self):
        print("cf", self.cleaned_data("febid"))
        return self.cleaned_data("febid")


class FebIDField(models.CharField):

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 18
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        return name, path, args, kwargs

    def from_db_value(self, value, expression, conection):
        return "0x{:s}".format(value.lower())

    def get_prep_value(self, value):
        return parse_hex(value)

    def to_python(self, value):
        return value

    def formfield(self, **kwargs):
        defaults = {"form_class": HexFormField}
        defaults.update(kwargs)
        # Use the Field base method without super to skip the validation of the
        # PositiveInterField
        return models.fields.Field.formfield(self, **kwargs)
        # return super().formfield(self, **kwargs)


class Card(models.Model):
    febid = FebIDField()
    name = models.CharField(max_length=32)
    notes = models.TextField(blank=True, default="")

    def __str__(self):
        return f"{self.febid} -- {self.name}"
        # return f"{self.febid}"
