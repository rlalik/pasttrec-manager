from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views import generic

import json  # , pasttrec

from ..models import Card, CardSettings, Connection, Revision, Setup, TDC
from ..forms import ConnectionForm
from ..querysets import queryset_for_card_field


# Create your views here.
def add_connection_view(request, rev=None, tdc=None):
    if request.method == "POST":
        instance = Connection.objects.get(revision__pk=rev, tdc__pk=tdc)
        form = ConnectionForm(request.POST, instance=instance)

        if form.is_valid():
            form.save()
            return redirect("django_pasttrec_manager:setup", instance.revision.setup.pk)
        else:
            return redirect("django_pasttrec_manager:add_connection")

    else:
        instance = Connection.objects.get(revision__pk=pk, tdc__pk=tdc)

        s_rev = 1 if rev else 0
        s_tdc = 2 if tdc else 0
        initial = {"step": s_rev | s_tdc, "revision": rev, "tdc": tdc}

        form = ConnectionForm(initial=initial, instance=instance)
        form.fields["card1"].queryset = queryset_for_card_field("", request, rev, tdc)
        form.fields["card2"].queryset = queryset_for_card_field("", request, rev, tdc)
        form.fields["card3"].queryset = queryset_for_card_field("", request, rev, tdc)

        return render(
            request,
            "django_pasttrec_manager/card_connection.html",
            context={
                "form": form,
            },
        )


def insert_connection_view(request, rev=None, tdc=None):
    if request.method == "POST":
        form = ConnectionForm(request.POST)

        if form.is_valid():
            form.save()
            revision = Revision.objects.get(pk=rev)
            return redirect("django_pasttrec_manager:setup", revision.setup.pk)
        else:
            return redirect("django_pasttrec_manager:insert_connection", rev, tdc)

    else:
        try:
            revision = Revision.objects.get(pk=rev)

        except Revision.DoesNotExist:
            revision = None

        if revision:
            result = Connection.objects.filter(
                revision__setup=revision.setup, tdc=tdc, revision__creation_on__lte=revision.creation_on
            ).order_by("-revision__creation_on")

        if result:
            if result[0].revision.pk == rev:
                return redirect("django_pasttrec_manager:change_connection", result[0].pk)

            form = ConnectionForm(instance=result[0], initial={"step": 0, "revision": rev})
        else:
            form = ConnectionForm(initial={"step": 0, "revision": rev})

        form.fields["card1"].queryset = queryset_for_card_field("", request, rev, tdc)
        form.fields["card2"].queryset = queryset_for_card_field("", request, rev, tdc)
        form.fields["card3"].queryset = queryset_for_card_field("", request, rev, tdc)

        return render(
            request,
            "django_pasttrec_manager/insert_connection.html",
            context={
                "form": form,
                "revision": revision,
                "tdc": tdc,
            },
        )


def delete_connection_view(request, pk=None):
    if request.method == "POST":
        try:
            instance = Connection.objects.get(pk=pk)
            instance.delete()
            return redirect("django_pasttrec_manager:setup", instance.revision.setup.pk)

        except Connection.DoesNotExist:
            return redirect("django_pasttrec_manager:index")

        pass

    else:
        try:
            instance = Connection.objects.get(pk=pk)
        except Connection.DoesNotExist:
            return redirect("django_pasttrec_manager:index")

        return render(
            request,
            "django_pasttrec_manager/remove_connection.html",
            context={
                "connection": instance,
            },
        )


# Create your views here.
def edit_connection_view(request, pk):
    if request.method == "POST":
        instance = Connection.objects.get(pk=pk)
        form = ConnectionForm(request.POST, instance=instance)

        if form.is_valid():
            form.save()
            return redirect("django_pasttrec_manager:setup", instance.revision.setup.pk)
        else:
            return redirect("django_pasttrec_manager:edit_connection")

    else:
        q_c = Connection.objects.get(pk=pk)
        initial = {
            "step": 7,
        }

        form = ConnectionForm(initial=initial, instance=q_c)
        form.fields["card1"].queryset = queryset_for_card_field("", request, q_c.revision.pk, q_c.tdc.pk)
        form.fields["card2"].queryset = queryset_for_card_field("", request, q_c.revision.pk, q_c.tdc.pk)
        form.fields["card3"].queryset = queryset_for_card_field("", request, q_c.revision.pk, q_c.tdc.pk)

        return render(
            request,
            "django_pasttrec_manager/card_connection.html",
            context={
                "form": form,
                "connection_pk": pk,
                "revision_pk": q_c.revision.pk,
                "tdc_pk": q_c.tdc.pk,
            },
        )
