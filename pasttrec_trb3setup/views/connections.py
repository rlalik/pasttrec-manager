from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views import generic

import json, pasttrec

from ..models import Card, CardSettings, Connection, Revision, Setup, TDC
from ..forms import ConnectionForm
from ..querysets import queryset_for_card_field

# Create your views here.
def add_connection_view(request, rev=None, tdc=None):
    if request.method == 'POST':
        form = ConnectionForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('pasttrec_trb3setup:index')
        else:
            return redirect('pasttrec_trb3setup:add_connection')

    else:
        s_rev = 1 if rev else 0
        s_tdc = 2 if tdc else 0
        initial = { 'step' : s_rev | s_tdc, 'revision' : rev, 'tdc' : tdc }

        form = ConnectionForm(initial=initial)
        form.fields['card1'].queryset = queryset_for_card_field('', request, rev, tdc)
        form.fields['card2'].queryset = queryset_for_card_field('', request, rev, tdc)
        form.fields['card3'].queryset = queryset_for_card_field('', request, rev, tdc)

        return render(
            request,
            'pasttrec_trb3setup/add_connection.html',
            context = {
                'form' : form,
            }
        );

# Create your views here.
def edit_connection_view(request, pk):
    if request.method == 'POST':
        form = ConnectionForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('pasttrec_trb3setup:index')
        else:
            return redirect('pasttrec_trb3setup:edit_connection')

    else:
        q_c = Connection.objects.get(pk=pk)
        initial = {
            'step' : 7,
            'revision' : q_c.revision,
            'tdc' : q_c.tdc,
            'card1' : q_c.card1,
            'card2' : q_c.card2,
            'card3' : q_c.card3,
            }

        form = ConnectionForm(initial=initial)
        form.fields['card1'].queryset = queryset_for_card_field('', request, q_c.revision.pk, q_c.tdc.pk)
        form.fields['card2'].queryset = queryset_for_card_field('', request, q_c.revision.pk, q_c.tdc.pk)
        form.fields['card3'].queryset = queryset_for_card_field('', request, q_c.revision.pk, q_c.tdc.pk)

        return render(
            request,
            'pasttrec_trb3setup/add_connection.html',
            context = {
                'form' : form,
            }
        );
