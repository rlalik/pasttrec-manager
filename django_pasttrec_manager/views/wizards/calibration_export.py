# from django.core.exceptions import DoesNotExist
from django.core.files.storage import DefaultStorage, InMemoryStorage
from django.forms.models import model_to_dict
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404

from django.urls import reverse

from django_pasttrec_manager.models import (
    AsicConfiguration,
    AsicBaselineSettings,
    Card,
    CardCalibration,
    CardsSetup,
)
from django_pasttrec_manager.forms import (
    SetupAndConfigurationForExportCalibration,
    SelectCardsForExportCalibration,
)
from django_pasttrec_manager.tools import safe_serialize, disable_form_fields

import json

from formtools.wizard.views import SessionWizardView


class CalibrationExportWizardView(SessionWizardView):
    # template_name = "django_pasttrec_manager/calibration_json_wizard.html"

    form_list = [
        ("setup_and_config", SetupAndConfigurationForExportCalibration),
        ("select_cards", SelectCardsForExportCalibration),
    ]

    TEMPLATES = {
        "setup_and_config": "django_pasttrec_manager/wizards/general_page.html",
        "select_cards": "django_pasttrec_manager/wizards/general_page.html",
    }

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        context.update(
            {
                "wizard_title": "Calibration export wizard",
                "form_url": "django_pasttrec_manager:export_calibration_wizard",
            },
        )

        if self.steps.current == "setup_and_config":
            context.update({"slide_title": "Select configuration and cards setup to export"})

        if self.steps.current == "select_cards":
            context.update({"slide_title": "Confirm cards to be exported"})

        return context

    def import_payload_into_session(self, file):
        payload_str = b""
        for chunk in file:
            payload_str += chunk

        decoded = json.loads(payload_str.decode())

        import_tree = self.request.session["import_tree"] = {
            "cards": {},
            "configs": {},
            "calibrations": [],
            "baselines": {},
        }

        for febid, data in decoded.items():
            feb_data = {}

            # Get cards info
            try:
                card_obj = Card.objects.get(febid=febid)
            except Card.DoesNotExist:
                card_obj = Card(febid=febid)

            import_tree["cards"][febid] = [
                model_to_dict(card_obj),
            ]

            # Get configurations info
            bl_data_0 = data[0].pop("baselines", None)
            cfg_data_0 = data[0]

            bl_data_1 = data[1].pop("baselines", None)
            cfg_data_1 = data[1]

            if cfg_data_0 != cfg_data_1:
                raise ValueError("Both ASICs must have same configuration")
            try:
                config_obj = AsicConfiguration.objects.get(**cfg_data_0)
            except AsicConfiguration.DoesNotExist:
                config_obj = AsicConfiguration(**cfg_data_0)

            acs_hash = str(config_obj.__hash__())
            import_tree["configs"][acs_hash] = [
                model_to_dict(config_obj),
                febid,
            ]

            # Get ASICs info
            asics = import_tree["baselines"][febid] = {}

            def play_with_asic(data):
                try:
                    reference = AsicBaselineSettings.make_object(data)
                    abs_obj = AsicBaselineSettings.objects.get(
                        **model_to_dict(reference)
                    )
                except AsicBaselineSettings.DoesNotExist:
                    abs_obj = reference

                return acs_hash, abs_obj.id, model_to_dict(abs_obj)

            asics["0"] = play_with_asic(bl_data_0)
            asics["1"] = play_with_asic(bl_data_1)

            # Check for already existing calibrations.
            # Requires that card and configuration already exists

            try:
                cardcalib_obj = CardCalibration.objects.get(
                    card=card_obj, config=config_obj
                )
                import_tree["calibrations"].append(
                    ((card_obj.febid, str(config_obj.__hash__())), True)
                )
            except CardCalibration.DoesNotExist:
                import_tree["calibrations"].append(
                    ((card_obj.febid, str(config_obj.__hash__())), False)
                )
            except ValueError:
                import_tree["calibrations"].append(
                    ((card_obj.febid, str(config_obj.__hash__())), None)
                )

        return import_tree

    @staticmethod
    def init_kwargs(model, arg_dict):
        model_fields = [f.name for f in model._meta.get_fields() if f.name != "id"]
        return {k: v for k, v in arg_dict.items() if k in model_fields}

    def get_form_initial(self, step):
        print(step)
        if step == "select_cards":

            preselection_data = self.get_cleaned_data_for_step("setup_and_config")
            print(preselection_data)

            config_data = get_object_or_404(AsicConfiguration, pk=preselection_data['configuration'])
            print(config_data)

            if int(preselection_data['setup']) > 0:
                cardcalib_data = get_list_or_404(CardCalibration, config=config_data)
            else:
                cardcalib_data = get_list_or_404(CardCalibration, config=config_data)

            return [
                cd.card
                for cd in cardcalib_data
            ]

        if step == "calibrations":
            import_tree = self.request.session["import_tree"]

            cards_data = self.get_cleaned_data_for_step("cards")
            for cd in cards_data:
                card_obj = Card(**cd)
                import_tree["cards"][str(card_obj.febid)][0] = model_to_dict(card_obj)

            configurations_data = self.get_cleaned_data_for_step("configurations")
            for cd in configurations_data:
                config_obj = AsicConfiguration(**cd)
                config_hash = str(config_obj.__hash__())
                import_tree["configs"][str(config_hash)][0] = model_to_dict(config_obj)

            initials = []
            for existing_calib in import_tree["calibrations"]:
                must_be_new = False
                try:
                    card_obj = Card.objects.get(febid=existing_calib[0][0])
                except Card.DoesNotExist:
                    card_obj = Card(**import_tree["cards"][existing_calib[0][0]][0])
                    must_be_new = True

                try:
                    config_obj = AsicConfiguration.objects.get(
                        id=import_tree["configs"][existing_calib[0][1]][0]["id"]
                    )
                except AsicConfiguration.DoesNotExist:
                    config_obj = AsicConfiguration(
                        **import_tree["configs"][existing_calib[0][1]][0]
                    )
                    must_be_new = True

                if must_be_new is not True:
                    try:
                        calib_obj = CardCalibration.objects.get(
                            card=card_obj, config=config_obj
                        )
                        asic0_old_obj = calib_obj.asic0
                        asic1_old_obj = calib_obj.asic1
                    except CardCalibration.DoesNotExist:
                        calib_obj = CardCalibration(card=card_obj, config=config_obj)
                        asic0_old_obj = None
                        asic1_old_obj = None
                else:
                    calib_obj = CardCalibration(card=card_obj, config=config_obj)
                    asic0_old_obj = None
                    asic1_old_obj = None

                asic0_new_obj = AsicBaselineSettings(
                    **import_tree["baselines"][existing_calib[0][0]]["0"][2]
                )
                asic1_new_obj = AsicBaselineSettings(
                    **import_tree["baselines"][existing_calib[0][0]]["1"][2]
                )

                initials.append(
                    {
                        "card_id": model_to_dict(card_obj),
                        "config_id": model_to_dict(config_obj),
                        "calib_id": model_to_dict(calib_obj),
                        "asic0_id": (
                            model_to_dict(asic0_new_obj) if asic0_new_obj else None
                        ),
                        "asic1_id": (
                            model_to_dict(asic1_new_obj) if asic1_new_obj else None
                        ),
                        "asic0_old_id": (
                            model_to_dict(asic0_old_obj) if asic0_old_obj else None
                        ),
                        "asic1_old_id": (
                            model_to_dict(asic1_old_obj) if asic1_old_obj else None
                        ),
                    }
                )

            return initials

        return self.initial_dict.get(step, {})

    def done(self, form_list, **kwargs):
        payload_data = self.get_payload_data()

        dict_config = {}

        for febid, v in payload_data.items():

            # Get cards info
            try:
                card_obj = Card.objects.get(febid=febid)
            except Card.DoesNotExist:
                cards_data = import_tree["cards"][febid]
                card_obj = Card(**self.init_kwargs(Card, cards_data[0]))
                card_obj.save()

            for _, config_data in import_tree["configs"].items():
                if config_data[1] == febid:
                    try:
                        config_obj = AsicConfiguration.objects.get(**config_data[0])
                    except AsicConfiguration.DoesNotExist:
                        config_obj = AsicConfiguration(**config_data[0])
                        config_obj.save()

            asics = import_tree["baselines"][febid]

            try:
                calib_obj = CardCalibration.objects.get(
                    card=card_obj, config=config_obj
                )

                def update_baselines(asic_bl_id, data):
                    instance, created = AsicBaselineSettings.objects.get_or_create(
                        id=asic_bl_id
                    )
                    if not created:
                        data.pop("id")
                        for attr, value in data.items():
                            setattr(instance, attr, value)
                        instance.save()

                update_baselines(calib_obj.asic0.id, asics["0"][2])
                update_baselines(calib_obj.asic1.id, asics["1"][2])

            except CardCalibration.DoesNotExist:
                asic0_obj = AsicBaselineSettings(**asics["0"][2])
                asic0_obj.save()

                asic1_obj = AsicBaselineSettings(**asics["1"][2])
                asic1_obj.save()

                calib_obj = CardCalibration(
                    card=card_obj, config=config_obj, asic0=asic0_obj, asic1=asic1_obj
                )
                calib_obj.save()

        return redirect(reverse("django_pasttrec_manager:index"))
