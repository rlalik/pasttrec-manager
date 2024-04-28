from django.db.models import Q
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic

from ..models import AsicConfiguration, AsicBaselineSettings, Card, CardCalibration
from ..forms import CardForm
# , CardInsertMultipleForm, AsicConfigSettingsForm, AsicBaselineSettingsForm
# , CardSettingsMassChangeForm, RevisionForm
from ..forms import AsicConfigurationForm, AsicBaselineSettingsForm
from .views import create_revision_snapshot, find_last_card_revision, IndexView


class CardView(generic.DetailView):
    model = Card
    template_name = "django_pasttrec_manager/card_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        card_id = self.kwargs.get("pk", None)

        calibrations = CardCalibration.objects.filter(card=card_id)

        context["calibrations"] = calibrations

        return context


class CardsView(IndexView):
    # template_name = "django_pasttrec_manager/cards.html"
    #
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     cards = Card.objects.order_by("name")
    #     cards_and_settings = []
    #     for c in cards:
    #         cards_and_settings.append({"card": c, "num_settings": CardSettings.objects.filter(card=c.pk).count()})
    #     context["cards"] = cards_and_settings
    #     return context
    pass


def insert_card_view(request, name=None, febid=None):
    if name is not None and febid is not None:
        if request.user.is_authenticated:
            obj, created = Card.objects.update_or_create(febid=febid, name=name)
            return redirect("django_pasttrec_manager:card", obj.pk)
        else:
            return HttpResponse("Unauthorized", status=401)

    elif (name is None) is not (febid is None):
        return HttpResponse("Incorrect data", status=405)

    if request.method == "POST":
        form = CardInsertForm(request.POST)

        if form.is_valid():
            obj, created = Card.objects.update_or_create(
                febid=form.cleaned_data["febid"], name=form.cleaned_data["name"], notes=form.cleaned_data["notes"]
            )
            return redirect("django_pasttrec_manager:index")

        return render(
            request,
            "django_pasttrec_manager/insert_card.html",
            context={
                "form": form,
            },
        )

    else:
        form = CardInsertForm()
        return render(
            request,
            "django_pasttrec_manager/insert_card.html",
            context={
                "form": form,
            },
        )


def insert_cards_view(request, names=None):
    if request.method == "POST":
        form = CardInsertMultipleForm(request.POST)

        if form.is_valid():
            names = form.cleaned_data["name"].split(",")
            notes = form.cleaned_data["notes"]
            for n in names:
                obj, created = Card.objects.update_or_create(name=n, notes=notes)
            return redirect("django_pasttrec_manager:index")
        else:
            return redirect("django_pasttrec_manager:insert_cards")

    else:
        form = CardInsertMultipleForm()
        return render(
            request,
            "django_pasttrec_manager/insert_cards.html",
            context={
                "form": form,
            },
        )
