from django.shortcuts import render, redirect
from django.views import generic

from ..models import AsicConfiguration, AsicBaselineSettings, Card, CardCalibration

import json
from enum import Enum


class IndexView(generic.ListView):
    """
    The index page view.
    """

    template_name = "django_pasttrec_manager/index.html"

    def get_queryset(self):
        return None
        return AsicConfiguration.objects.order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        setup_id = self.kwargs.get("setup_id", None)
        context["configurations"] = AsicConfiguration.objects.order_by("name")
        context["cards"] = Card.objects.order_by("name")
        return context


class CardView(generic.DetailView):
    model = Card
    template_name = "django_pasttrec_manager/card_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        card_id = self.kwargs.get("pk", None)

        calibrations = CardCalibration.objects.filter(card=card_id)

        context["calibrations"] = calibrations

        return context


class AsicConfigurationView(generic.ListView):
    model = AsicConfiguration
    template_name = "django_pasttrec_manager/configuration.html"

    def get_queryset(self, **kwargs):
        config_id = self.kwargs.get("config_id", None)
        return CardCalibration.objects.filter(config__id=config_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config_id = self.kwargs.get("config_id", None)
        configuration = AsicConfiguration.objects.get(pk=config_id)

        context["configuration"] = configuration
        context["calibrations"] = CardCalibration.objects.filter(config=configuration)

        return context


class CardCalibrationView(generic.DetailView):
    model = CardCalibration
    template_name = "django_pasttrec_manager/card_calibration_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        card_id = self.kwargs.get("pk", None)

        calibrations = CardCalibration.objects.filter(card=card_id)

        context["calibrations"] = calibrations

        return context
