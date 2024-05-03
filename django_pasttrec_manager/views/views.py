from django.shortcuts import render, redirect
from django.views import generic

from ..models import (
    AsicConfiguration,
    AsicBaselineSettings,
    Card,
    CardCalibration,
    CardsSetup,
)
from ..forms import CardsSetupForm

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
        context["cards_setups"] = CardsSetup.objects.order_by("name")
        return context


class CardsView(generic.ListView):
    model = Card
    template_name = "django_pasttrec_manager/cards.html"


class CardView(generic.DetailView):
    model = Card
    template_name = "django_pasttrec_manager/card.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get("pk", None)
        context["calibrations"] = CardCalibration.objects.filter(card=pk)
        context["cards_setups"] = CardsSetup.objects.order_by("name")
        return context


class AsicConfigurationView(generic.ListView):
    model = AsicConfiguration
    template_name = "django_pasttrec_manager/configuration.html"

    def get_queryset(self, **kwargs):
        pk = self.kwargs.get("pk", None)
        return CardCalibration.objects.filter(config__id=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get("pk", None)
        context["configuration"] = AsicConfiguration.objects.get(pk=pk)
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


class CardsSetupView(generic.ListView):
    model = CardsSetup
    template_name = "django_pasttrec_manager/cards_setup.html"

    def get_queryset(self, **kwargs):
        pk = self.kwargs.get("pk", None)
        return Card.objects.filter(cardssetup__pk=pk).order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get("pk", None)
        cards_setup = CardsSetup.objects.get(pk=pk)
        context["cards_setup"] = cards_setup
        return context


def add_cards_setup_view(request):
    # if request.user.is_authenticated:
    #     obj, created = Card.objects.update_or_create(febid=febid, name=name)
    #     return redirect("django_pasttrec_manager:card", obj.pk)
    # else:
    #     return HttpResponse("Unauthorized", status=401)

    if request.method == "POST":
        form = CardsSetupForm(request.POST)

        if form.is_valid():
            print(form.cleaned_data)
            obj, created = CardsSetup.objects.update_or_create(
                name=form.cleaned_data["name"]
            )
            for card in form.cleaned_data["cards"]:
                obj.cards.add(card)
            obj.save()

            return redirect("django_pasttrec_manager:cards_setup", obj.pk)

        return render(
            request,
            "django_pasttrec_manager/add_cards_setup.html",
            context={
                "form": form,
            },
        )

    else:
        form = CardsSetupForm()
        return render(
            request,
            "django_pasttrec_manager/add_cards_setup.html",
            context={
                "form": form,
            },
        )
