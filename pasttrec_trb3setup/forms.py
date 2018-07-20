from django import forms
from django.core.validators import FileExtensionValidator
import datetime, json

from .models import Revision, Card

class RevisionForm(forms.ModelForm):
    creation_on = forms.SplitDateTimeField(initial=datetime.datetime.now, widget=forms.SplitDateTimeWidget)
    class Meta:
        model = Revision
        fields = [ 'setup', 'creation_on' ]

class JsonUploadFileForm(forms.Form):
    file = forms.FileField()
    #validators=[FileExtensionValidator(allowed_extensions=['json'])]

class CardConfigInsertForm(forms.Form):
    raw_data = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        raw = kwargs.pop('raw', None)
        extra = kwargs.pop('extra', None)
        super().__init__(*args, **kwargs)
        self.initial['raw_data'] = raw

        if extra is not None:
            for v in extra:
                parts = v['name'].split('_')
                self.fields[v['name']] = \
                    forms.ModelChoiceField(
                        queryset=(Card.objects.all()),
                        label="Id: {:s}  Cable: {:s}".format(parts[1], parts[2]),
                        required=False
                    )
                #self.initial[v['name']] = v

    def clean(self):
        pass
