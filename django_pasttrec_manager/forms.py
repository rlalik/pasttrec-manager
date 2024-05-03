from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.forms import formset_factory
from django.forms import BaseFormSet

from django_pasttrec_manager.models import (
    AsicConfiguration,
    AsicBaselineSettings,
    Card,
    CardCalibration,
    CardsSetup,
)
from django_pasttrec_manager.tools import disable_form_fields

import datetime
import json


class JsonUploadFileForm(forms.Form):
    @staticmethod
    def validate_file_extension(value):
        if not value.name.endswith(".json"):
            raise ValidationError("Must be json file")

    file = forms.FileField(validators=[validate_file_extension])


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


class CardCalibrationActionsForm(forms.Form):
    """
    Provides overview of the FEB card, setup and baseline settings for given calibration.
    It presents the previous and next baseline values, and has an check box to mark the
    calibration for overwritting.
    """

    template_name = "django_pasttrec_manager/forms/card_calibration_actions_form.html"

    confirm_actions = forms.BooleanField(
        label="Confirm these actions",
        required=False,
        initial=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        initial = kwargs.get("initial")

        card_obj_id = initial["card_id"]["id"]
        config_obj_id = initial["config_id"]["id"]
        calib_obj_id = initial["calib_id"]["id"]
        asic0_new_obj_id = initial["asic0_id"]["id"] if initial["asic0_id"] else None
        asic1_new_obj_id = initial["asic1_id"]["id"] if initial["asic1_id"] else None
        asic0_old_obj_id = (
            initial["asic0_old_id"]["id"] if initial["asic0_old_id"] else None
        )
        asic1_old_obj_id = (
            initial["asic1_old_id"]["id"] if initial["asic1_old_id"] else None
        )

        setattr(self, "asic0_obj_id", asic0_new_obj_id)
        setattr(self, "asic1_obj_id", asic1_new_obj_id)

        new_calib = card_obj_id is None or config_obj_id is None

        actions = []
        if card_obj_id is None:
            actions.append("This will add new FEB Card.")

        if config_obj_id is None:
            actions.append("This will add new FEB Configuration.")

        if asic0_new_obj_id is None:
            if asic0_old_obj_id is None:
                actions.append("This will add new ASIC 0 baselines.")
            else:
                actions.append("This will overwrite ASIC 0 baselines.")

        if asic1_new_obj_id is None:
            if asic1_old_obj_id is None:
                actions.append("This will add new ASIC 1 baselines.")
            else:
                actions.append("This will overwrite ASIC 1 baselines.")

        if calib_obj_id is None:
            actions.append(
                "This will add new baselines calibration "
                "for given card and configuration"
            )

        setattr(self, f"actions", actions)

        def update_widgets(name, form, template=None, extras=None):
            if extras is None:
                extras = {}

            new_form = form(prefix=self.prefix, initial=initial[f"{name}_id"], **extras)
            if template:
                new_form.template_name = template
            setattr(self, f"{name}_form", new_form)

        update_widgets(
            "card",
            CardForm,
            "django_pasttrec_manager/forms/card_form_view.html",
            extras={"insert_new": card_obj_id is None},
        )
        update_widgets(
            "config",
            AsicConfigurationForm,
            "django_pasttrec_manager/forms/asic_configuration_form_view.html",
            extras={"insert_new": config_obj_id is None},
        )

        update_widgets(
            "asic0",
            AsicBaselineSettingsForm,
            "django_pasttrec_manager/forms/asic_baseline_minimal_form_view.html",
            extras={"asic_no": 0, "insert_new": asic0_new_obj_id is None},
        )
        update_widgets(
            "asic1",
            AsicBaselineSettingsForm,
            "django_pasttrec_manager/forms/asic_baseline_minimal_form_view.html",
            extras={"asic_no": 1, "insert_new": asic0_new_obj_id is None},
        )

        if asic0_old_obj_id:
            update_widgets(
                "asic0_old",
                AsicBaselineSettingsForm,
                "django_pasttrec_manager/forms/asic_baseline_minimal_form_view.html",
                extras={"asic_no": 0, "insert_new": asic0_new_obj_id is None},
            )
        if asic1_old_obj_id:
            update_widgets(
                "asic1_old",
                AsicBaselineSettingsForm,
                "django_pasttrec_manager/forms/asic_baseline_minimal_form_view.html",
                extras={"asic_no": 1, "insert_new": asic0_new_obj_id is None},
            )


CardCalibrationActionsFormSet = formset_factory(CardCalibrationActionsForm, extra=0)


class BaseCardCalibrationFormSet(BaseFormSet):
    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        print("+++ BaseCardCalibrationFormSet:", index, kwargs)
        if "card_info" in kwargs:
            kwargs["card_info"] = kwargs["card_info"][index]
        if "config_info" in kwargs:
            kwargs["config_info"] = kwargs["config_info"][index]
        if "asic0_info" in kwargs:
            kwargs["asic0_info"] = kwargs["asic0_info"][index]
        if "asic1_info" in kwargs:
            kwargs["asic1_info"] = kwargs["asic1_info"][index]
        return kwargs


class AsicSettingsMassChangeForm(forms.Form):
    threshold = forms.IntegerField(min_value=0, max_value=31, required=False)
    tc1c = forms.IntegerField(min_value=0, max_value=3, required=False)
    tc1r = forms.IntegerField(min_value=0, max_value=3, required=False)
    tc2c = forms.IntegerField(min_value=0, max_value=3, required=False)
    tc2r = forms.IntegerField(min_value=0, max_value=3, required=False)


class CardForm(forms.ModelForm):
    template_name = "django_pasttrec_manager/forms/card_form.html"

    class Meta:
        model = Card
        fields = ["febid", "name", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 2, "cols": "auto"}),
        }

    def __init__(self, *args, **kwargs):
        self.insert_new = kwargs.pop("insert_new", None)
        super().__init__(*args, **kwargs)


CardFormSet = formset_factory(CardForm, extra=0)


class CardInsertMultipleForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ["febid", "name", "notes"]
        widgets = {
            "name": forms.Textarea(attrs={"cols": 80, "rows": 5}),
        }


class CardsSetupForm(forms.ModelForm):
    template_name = "django_pasttrec_manager/forms/cards_setup_form.html"

    class Meta:
        model = CardsSetup
        fields = "__all__"


class AddCardToExistingSetupForm(forms.Form):
    """
    Provides overview of the FEB card, setup and baseline settings for given calibration.
    It presents the previous and next baseline values, and has an check box to mark the
    calibration for overwritting.
    """

    template_name = "django_pasttrec_manager/forms/cards_setup_actions_form.html"

    confirm_actions = forms.BooleanField(
        label="Add to setups",
        required=False,
        initial=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        initial = kwargs.get("initial")
        card_obj_id = initial["card_id"]["id"]

        def update_widgets(name, form, template=None, extras=None):
            if extras is None:
                extras = {}

            new_form = form(prefix=self.prefix, initial=initial[f"{name}_id"], **extras)
            if template:
                new_form.template_name = template
            setattr(self, f"{name}_form", new_form)
            return new_form

        f = update_widgets(
            "card",
            CardForm,
            # "django_pasttrec_manager/forms/card_form_view.html",
            extras={"insert_new": card_obj_id is None},
        )

        disable_form_fields(f, enabled_fields=())


AddCardToExistingSetupFormSet = formset_factory(AddCardToExistingSetupForm, extra=0)


class NewOrExistingCardsSetupForm(forms.Form):
    """
    This forms asks for new cards setup name and/or allows to select existing cards setup.
    """

    template_name = (
        "django_pasttrec_manager/forms/new_or_existing_cards_setup_form.html"
    )

    new_setup_name = forms.CharField(max_length=100, required=False)
    existing_setup = forms.MultipleChoiceField(
        choices=(lambda setup_objs: [(obj.pk, obj) for obj in setup_objs])(
            CardsSetup.objects.all()
        ),
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        nsn = cleaned_data.get("new_setup_name")
        exs = cleaned_data.get("existing_setup")

        if len(exs) == 0 and len(nsn) == 0:
            raise ValidationError(
                f"Either existing setup must be selected or new one provided"
            )
