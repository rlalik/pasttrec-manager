from django import forms
from django.core.exceptions import ValidationError

from django_pasttrec_manager.models import CardsSetup
from django_pasttrec_manager.tools import disable_form_fields


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


AddCardToExistingSetupFormSet = forms.formset_factory(
    AddCardToExistingSetupForm, extra=0
)


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
