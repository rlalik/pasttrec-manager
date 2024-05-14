from django import forms
from django.core.exceptions import ValidationError


class JsonUploadFileForm(forms.Form):
    @staticmethod
    def validate_file_extension(value):
        if not value.name.endswith(".json"):
            raise ValidationError("Must be json file")

    file = forms.FileField(validators=[validate_file_extension])
