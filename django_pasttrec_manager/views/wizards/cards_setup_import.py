# from django.core.exceptions import DoesNotExist
from django.core.files.storage import DefaultStorage, InMemoryStorage
from django.forms.models import model_to_dict
from django.shortcuts import render, redirect
from django.urls import reverse

from django_pasttrec_manager.models import Card, CardsSetup
from django_pasttrec_manager.forms import (
    JsonUploadFileForm,
    CardFormSet,
    AddCardToExistingSetupFormSet,
    NewOrExistingCardsSetupForm,
)
from django_pasttrec_manager.tools import safe_serialize, disable_form_fields

import json

from formtools.wizard.views import SessionWizardView


class CardsSetupsImportWizardView(SessionWizardView):
    file_storage = InMemoryStorage()

    form_list = [
        ("upload", JsonUploadFileForm),
        ("cards", CardFormSet),
        ("selection", AddCardToExistingSetupFormSet),
        ("cards_setup", NewOrExistingCardsSetupForm),
    ]

    TEMPLATES = {
        "upload": "django_pasttrec_manager/wizards/json_upload.html",
        "cards": "django_pasttrec_manager/wizards/general_page.html",
        "selection": "django_pasttrec_manager/wizards/general_page.html",
        "cards_setup": "django_pasttrec_manager/wizards/general_page.html",
    }

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]

    def get_payload_data(self):
        return self.request.session["import_payload"]

    def get_session_tree(self):
        return self.request.session["import_tree"]

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        context.update(
            {"form_url": "django_pasttrec_manager:import_cards_setups_wizard"}
        )
        return context

    def import_payload_into_session(self, file):
        payload_str = b""
        for chunk in file:
            payload_str += chunk

        decoded = json.loads(payload_str.decode())

        self.request.session["import_payload"] = decoded

        import_tree = self.request.session["import_tree"] = {
            "cards": {},
        }

        for trbid, data in decoded.items():
            for cable, febid in data.items():

                # Get cards info
                try:
                    card_obj = Card.objects.get(febid=febid)
                except Card.DoesNotExist:
                    card_obj = Card(febid=febid)

                import_tree["cards"][febid] = [model_to_dict(card_obj), trbid, cable]

        return import_tree

    @staticmethod
    def init_kwargs(model, arg_dict):
        model_fields = [f.name for f in model._meta.get_fields() if f.name != "id"]
        return {k: v for k, v in arg_dict.items() if k in model_fields}

    def get_form(self, step=None, data=None, files=None):
        # determine the step if not given
        if step is None:
            step = self.steps.current

        if step == "upload" and files is not None:
            self.import_payload_into_session(files["upload-file"])

        form = super().get_form(step, data, files)

        if step == "cards":
            for f in form:
                disable_form_fields(f, disabled_fields=("febid",))

        return form

    def get_form_initial(self, step):
        if step == "upload":
            return ()

        if step == "cards":
            import_tree = self.request.session["import_tree"]

            return [
                values[0]
                for _, values in import_tree["cards"].items()
                if values[0]["id"] is None
            ]

        if step == "selection":
            import_tree = self.request.session["import_tree"]
            cards_data = self.get_cleaned_data_for_step("cards")

            for cd in cards_data:
                card_obj = Card(**cd)
                import_tree["cards"][str(card_obj.febid)][0] = model_to_dict(card_obj)

            initials = []
            for febid, card_data in import_tree["cards"].items():
                card_obj = Card()
                try:
                    card_obj = Card.objects.get(febid=febid)
                except Card.DoesNotExist:
                    card_obj = Card(**card_data[0])

                initials.append(
                    {
                        "card_id": model_to_dict(card_obj),
                    }
                )

            return initials

        return self.initial_dict.get(step, {})

    def done(self, form_list, **kwargs):
        import_tree = self.get_session_tree()
        selection_data = self.get_cleaned_data_for_step("selection")
        cs_data = self.get_cleaned_data_for_step("cards_setup")

        dict_config = {}
        merged = tuple(
            zip(
                import_tree["cards"].items(), [tuple(x.items()) for x in selection_data]
            )
        )

        setups_to_add_card = []

        if cs_data["new_setup_name"]:
            cards_setup, created = CardsSetup.objects.get_or_create(
                name=cs_data["new_setup_name"]
            )
            setups_to_add_card.append(cards_setup)

        for existing_cs in cs_data["existing_setup"]:
            setups_to_add_card.append(CardsSetup.objects.get(pk=existing_cs))

        for data in merged:

            card_data = data[0][1][0]
            # Get cards info
            try:
                card_obj = Card.objects.get(febid=card_data["febid"])
            except Card.DoesNotExist:
                card_obj = Card(**self.init_kwargs(Card, card_data))
                card_obj.save()

            for cs in setups_to_add_card:
                cs.cards.add(card_obj)

        for cs in setups_to_add_card:
            cs.save()

        return redirect(reverse("django_pasttrec_manager:index"))
