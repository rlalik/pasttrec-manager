from django import forms
from django.core.validators import FileExtensionValidator
from django.forms import formset_factory

from django_pasttrec_manager.models import AsicConfiguration, AsicBaselineSettings
from django_pasttrec_manager.tools import disable_form_fields


class AsicConfigurationForm(forms.ModelForm):
    template_name = "django_pasttrec_manager/forms/asic_configuration_form.html"

    class Meta:
        model = AsicConfiguration
        fields = "__all__"
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 2, "cols": "auto"}),
        }

    def __init__(self, *args, **kwargs):
        self.insert_new = kwargs.pop("insert_new", None)
        disabled_fields = kwargs.pop("disabled_fields", None)
        enabled_fields = kwargs.pop("enabled_fields", None)
        super().__init__(*args, **kwargs)
        if disabled_fields or enabled_fields:
            disable_form_fields(self, disabled_fields, enabled_fields)


AsicConfigurationFormSet = formset_factory(AsicConfigurationForm, extra=0)


class AsicBaselineSettingsForm(forms.ModelForm):
    template_name = "django_pasttrec_manager/forms/asic_baseline_minimal_form.html"

    def __init__(self, *args, **kwargs):
        self.asic_no = kwargs.pop("asic_no", None)
        self.insert_new = kwargs.pop("insert_new", None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = AsicBaselineSettings
        fields = "__all__"


AsicBaselineSettingsFormSet = formset_factory(AsicBaselineSettingsForm, extra=0)


class AsicSettingsMassChangeForm(forms.Form):
    threshold = forms.IntegerField(min_value=0, max_value=31, required=False)
    tc1c = forms.IntegerField(min_value=0, max_value=3, required=False)
    tc1r = forms.IntegerField(min_value=0, max_value=3, required=False)
    tc2c = forms.IntegerField(min_value=0, max_value=3, required=False)
    tc2r = forms.IntegerField(min_value=0, max_value=3, required=False)
