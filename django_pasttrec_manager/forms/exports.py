from django import forms

from django_pasttrec_manager.models import AsicConfiguration, CardsSetup
from django_pasttrec_manager.tools import disable_form_fields

from . import AsicBaselineSettingsForm, AsicConfigurationForm, CardForm

class SetupAndConfigurationForExportCalibration(forms.Form):
    configuration = forms.ChoiceField(
        choices=(lambda setup_objs: [(obj.pk, obj) for obj in setup_objs])(
            AsicConfiguration.objects.all()
        ),
    )

    setup = forms.ChoiceField(
        choices=[(-1, "--- All available cards ---")]
        + [(obj.pk, obj) for obj in CardsSetup.objects.all()],
    )


class SelectCardsForExportCalibration(forms.Form):
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

        card_obj_id = kwargs.get("initial")
        print(card_obj_id)

        def update_widgets(name, form, template=None, extras=None):
            if extras is None:
                extras = {}

            new_form = form(prefix=self.prefix, initial=card_obj_id, **extras)
            if template:
                new_form.template_name = template
            setattr(self, f"{name}_form", new_form)
            return new_form

        f = update_widgets(
            "card",
            CardForm,
            # "django_pasttrec_manager/forms/card_form_view.html",
        )

        disable_form_fields(f, enabled_fields=())
