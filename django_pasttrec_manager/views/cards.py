from django.db.models import Q
from django.urls import reverse
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
import json  # , pasttrec

from ..models import Card, CardSettings, Connection, Revision, Setup, TDC
from ..forms import CardInsertForm, CardInsertMultipleForm, CardSettingsForm, CardSettingsMassChangeForm, RevisionForm
from .views import create_revision_snapshot, find_last_card_revision, IndexView

# Create your views here.


def get_card_or_top_map(c):
    if c is None:
        return None

    _c = c
    while True:
        if _c.map_to is None:
            return _c
        _c = _c.map_to


def in_map_chain(card, object):
    if card is None:
        return False

    _c = card
    while True:
        if _c == object:
            return True

        if _c.map_to is None:
            return False
        _c = _c.map_to


def card_view_lookup(request, id):
    obj = Card.objects.filter(name=id)
    if obj:
        return redirect("django_pasttrec_manager:card", obj.pk)

    obj = get_object_or_404(Card, febid=id)
    return redirect("django_pasttrec_manager:card", obj.pk)


class CardView(generic.DetailView):
    model = Card
    template_name = "django_pasttrec_manager/card_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        card_id = self.kwargs.get("pk", None)

        cards = CardSettings.objects.filter(card=card_id).order_by("-revision__creation_on")

        context["revisions"] = cards

        return context


class CardsView(IndexView):
    template_name = "django_pasttrec_manager/cards.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cards = Card.objects.order_by("name")
        cards_and_settings = []
        for c in cards:
            cards_and_settings.append({"card": c, "num_settings": CardSettings.objects.filter(card=c.pk).count()})
        context["cards"] = cards_and_settings
        return context


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


def add_settings_view(request, card_pk=None, rev_pk=None):
    if request.method == "POST":
        form = CardSettingsForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("django_pasttrec_manager:card", form.cleaned_data["card"].pk)
        else:
            return redirect("django_pasttrec_manager:add_settings")

    else:
        card = Card.objects.get(pk=card_pk)
        form = CardSettingsForm(
            initial={
                "card": card_pk,
                "revision": rev_pk,
            }
        )

        form.fields["map_to"].queryset = CardSettings.objects.filter(card=card)
        return render(
            request,
            "django_pasttrec_manager/card_settings_change.html",
            context={
                "card": card,
                "form": form,
                "form_rev": RevisionForm(),
                "redirect_to": reverse("django_pasttrec_manager:add_settings_by_card", args=[card_pk]),
            },
        )


def delete_settings_view(request, card_pk=None):
    if request.method == "POST":
        try:
            card = CardSettings.objects.get(pk=card_pk)
            card_id = card.card.pk
            card.delete()
            return redirect("django_pasttrec_manager:card", card_id)

        except CardSettings.DoesNotExist:
            return redirect("django_pasttrec_manager:index")

        pass

    else:
        try:
            card = CardSettings.objects.get(pk=card_pk)
        except CardSettings.DoesNotExist:
            return redirect("django_pasttrec_manager:index")

        return render(
            request,
            "django_pasttrec_manager/card_settings_remove.html",
            context={
                "card_revision": card,
            },
        )


def change_settings_view(request, pk):
    if request.method == "POST":
        instance = get_object_or_404(CardSettings, pk=pk)
        form = CardSettingsForm(request.POST, instance=instance)

        if form.is_valid():
            form.save()
            return redirect("django_pasttrec_manager:card", form.cleaned_data["card"].pk)
        else:
            return redirect("django_pasttrec_manager:change_settings", pk)

    else:
        cs = CardSettings.objects.get(pk=pk)
        all_cs = CardSettings.objects.exclude(pk=cs.pk).filter(card=cs.card)
        qq = Q(pk=cs.pk)
        for _cs in all_cs:
            test = in_map_chain(_cs, cs)
            if test:
                qq = qq | Q(pk=_cs.pk)

        form = CardSettingsForm(instance=cs)
        form.fields["map_to"].queryset = CardSettings.objects.filter(card=cs.card).exclude(qq)
        return render(
            request,
            "django_pasttrec_manager/card_settings_change.html",
            context={
                "settings": cs,
                "form": form,
                "redirect_to": reverse("django_pasttrec_manager:change_settings", args=[pk]),
            },
        )


def get_action_dict():
    return {"before": None, "action": None, "after": None}


class Action:
    COPY = "COPY"
    UPDATE = "UPDATE"


def test_card(revision, card):
    a = get_action_dict()
    if card is None:
        return None

    if card.revision != revision:
        a["before"] = card
        a["action"] = Action.COPY
        a["after"] = "NEW"
    else:
        a["before"] = card
        a["action"] = Action.UPDATE
        if card.map_to:
            a["after"] = "NEW from map"
        else:
            a["after"] = card

    return a


def change_settings_mass_view(request, rev):
    actions = []
    # prepare actions list
    revision = Revision.objects.get(pk=rev)
    snapshot = create_revision_snapshot(revision)

    for k, v in snapshot.items():
        a = test_card(revision, v["card1"])
        if a is not None:
            actions.append(a)
        a = test_card(revision, v["card2"])
        if a is not None:
            actions.append(a)
        a = test_card(revision, v["card3"])
        if a is not None:
            actions.append(a)

    if request.method == "POST":
        form = CardSettingsMassChangeForm(request.POST)

        if form.is_valid():
            threshold = request.POST["threshold"]
            tc1c = request.POST["tc1c"]
            tc1r = request.POST["tc1r"]
            tc2c = request.POST["tc2c"]
            tc2r = request.POST["tc2r"]

            for a in actions:
                c = a["before"]

                if c.map_to is not None:
                    old_pk = c.pk
                    c = get_card_or_top_map(c.map_to)
                    c.pk = old_pk
                    c.map_to = None

                c.revision = revision

                if threshold != "":
                    c.threshold_0 = threshold
                    c.threshold_1 = threshold

                if tc1c != "":
                    c.tc1c_0 = tc1c
                    c.tc1c_1 = tc1c

                if tc1r != "":
                    c.tc1r_0 = tc1r
                    c.tc1r_1 = tc1r

                if tc2c != "":
                    c.tc2c_0 = tc2c
                    c.tc2c_1 = tc2c

                if tc2r != "":
                    c.tc2r_0 = tc2r
                    c.tc2r_1 = tc2r

                if a["action"] == Action.COPY:
                    c.pk = None

                c.save()
            # form.save()
            # return redirect('django_pasttrec_manager:card', form.cleaned_data['card'].pk)
        # else:
        # print(request.POST)
        # return render(
        # request,
        #'django_pasttrec_manager/card_settings_mass.html',
        # context = {
        #'rev' : revision,
        #'form' : form,
        #'actions' : actions
        # }
        # );
        return redirect("django_pasttrec_manager:setup", revision.setup.pk)

    else:
        form = CardSettingsMassChangeForm()
        return render(
            request,
            "django_pasttrec_manager/card_settings_mass.html",
            context={
                "rev": revision,
                "form": form,
                "actions": actions,
            },
        )
