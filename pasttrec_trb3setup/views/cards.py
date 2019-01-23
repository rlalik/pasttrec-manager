from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
import json, pasttrec

from ..models import Card, CardSettings, Connection, Revision, Setup, TDC
from ..forms import CardInsertForm, CardInsertMultipleForm, CardSettingsForm, CardSettingsMassChangeForm, RevisionForm
from .views import create_revision_snapshot, find_last_card_revision

# Create your views here.

class CardView(generic.DetailView):
    model = Card
    template_name = 'pasttrec_trb3setup/card_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        card_id = self.kwargs.get('pk', None)

        cards = CardSettings.objects.filter(card=card_id).order_by('-revision__creation_on')

        context['revisions'] = cards

        return context

def insert_card_view(request):
    if request.method == 'POST':
        form = CardInsertForm(request.POST)

        if form.is_valid():
            obj, created = Card.objects.update_or_create(
                        name=form.cleaned_data['name'],
                        notes=form.cleaned_data['notes']
                    )
            return redirect('pasttrec_trb3setup:index')
        else:
            return redirect('pasttrec_trb3setup:insert_card')

    else:
        form = CardInsertForm()
        return render(
            request,
            'pasttrec_trb3setup/insert_card.html',
            context = {
                'form' : form,
            }
        );

def insert_cards_view(request):
    if request.method == 'POST':
        form = CardInsertMultipleForm(request.POST)

        if form.is_valid():
            names=form.cleaned_data['name'].split(',')
            notes=form.cleaned_data['notes']
            for n in names:
                obj, created = Card.objects.update_or_create(
                        name=n,
                        notes=notes
                    )
            return redirect('pasttrec_trb3setup:index')
        else:
            return redirect('pasttrec_trb3setup:insert_cards')

    else:
        form = CardInsertMultipleForm()
        return render(
            request,
            'pasttrec_trb3setup/insert_cards.html',
            context = {
                'form' : form,
            }
        );


def add_settings_view(request, card_pk=None, rev_pk=None):
    if request.method == 'POST':
        form = CardSettingsForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('pasttrec_trb3setup:card', form.cleaned_data['card'].pk)
        else:
            return redirect('pasttrec_trb3setup:add_settings')

    else:
        card = Card.objects.get(pk=card_pk)
        form = CardSettingsForm(initial={
            'card' : card_pk,
            'revision' : rev_pk,
            })
        return render(
            request,
            'pasttrec_trb3setup/card_settings_change.html',
            context = {
                'card' : card,
                'form' : form,
                'form_rev' : RevisionForm(),
                'redirect_to' : reverse('pasttrec_trb3setup:add_settings_by_card', args=[card_pk]),
            }
        );

def delete_settings_view(request, card_pk=None):
    if request.method == 'POST':
        try:
            card = CardSettings.objects.get(pk=card_pk)
            card_id = card.card.pk
            card.delete()
            return redirect('pasttrec_trb3setup:card', card_id)

        except CardSettings.DoesNotExist:
            return redirect('pasttrec_trb3setup:index')

        pass

    else:
        try:
            card = CardSettings.objects.get(pk=card_pk)
        except CardSettings.DoesNotExist:
            return redirect('pasttrec_trb3setup:index')

        return render(
            request,
            'pasttrec_trb3setup/card_settings_remove.html',
            context = {
                'card_revision' : card,
            }
        );

def change_settings_view(request, pk):
    if request.method == 'POST':
        instance = get_object_or_404(CardSettings, pk=pk)
        form = CardSettingsForm(request.POST, instance=instance)

        if form.is_valid():
            form.save()
            return redirect('pasttrec_trb3setup:card', form.cleaned_data['card'].pk)
        else:
            return redirect('pasttrec_trb3setup:change_settings', pk)

    else:
        cs = CardSettings.objects.get(pk=pk)
        form = CardSettingsForm(instance=cs)
        return render(
            request,
            'pasttrec_trb3setup/card_settings_change.html',
            context = {
                'settings' : cs,
                'form' : form,
                'redirect_to' : reverse('pasttrec_trb3setup:change_settings', pk),
            }
        );

def get_action_dict():
    return { 'before' : None, 'action' : None, 'after' : None }

class Action():
    COPY = 'COPY'
    UPDATE = 'UPDATE'

def test_card(revision, card):
    a = get_action_dict()
    if card is None:
        return None

    if card.revision != revision:
        a['before'] = card
        a['action'] = Action.COPY
        a['after'] = 'NEW'
    else:
        a['before'] = card
        a['action'] = Action.UPDATE
        a['after'] = card

    return a

def change_settings_mass_view(request, rev):
    actions = []
    # prepare actions list
    revision = Revision.objects.get(pk=rev)
    snapshot = create_revision_snapshot(revision)

    print(revision, snapshot)
    for k, v in snapshot.items():
        a = test_card(revision, v['card1'])
        if a is not None:
            actions.append(a)
        a = test_card(revision, v['card2'])
        if a is not None:
            actions.append(a)
        a = test_card(revision, v['card3'])
        if a is not None:
            actions.append(a)

    if request.method == 'POST':
        form = CardSettingsMassChangeForm(request.POST)

        if form.is_valid():
            print(request.POST)

            threshold = request.POST['threshold']
            for a in actions:
                c = a['before']
                c.revision = revision

                if threshold is not '':
                    c.threshold_0 = threshold
                    c.threshold_1 = threshold

                print(c)
                if a['action'] == Action.COPY:
                    c.pk = None

                c.save()
            #form.save()
            #return redirect('pasttrec_trb3setup:card', form.cleaned_data['card'].pk)
        #else:
        #print(request.POST)
        #return render(
            #request,
            #'pasttrec_trb3setup/card_settings_mass.html',
            #context = {
                #'rev' : revision,
                #'form' : form,
                #'actions' : actions
            #}
        #);
        return redirect('pasttrec_trb3setup:setup', revision.setup.pk)

    else:
        form = CardSettingsMassChangeForm()
        return render(
            request,
            'pasttrec_trb3setup/card_settings_mass.html',
            context = {
                'rev' : revision,
                'form' : form,
                'actions' : actions,
            }
        );
