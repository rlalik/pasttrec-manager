from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
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


def add_settings_view(request, card=None, rev=None):
    if request.method == 'POST':
        form = CardSettingsForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('pasttrec_trb3setup:card', form.cleaned_data['card'].pk)
        else:
            return redirect('pasttrec_trb3setup:add_settings')

    else:
        form = CardSettingsForm(initial={
            'card' : card,
            'revision' : rev,
            })
        return render(
            request,
            'pasttrec_trb3setup/card_settings.html',
            context = {
                'form' : form,
            }
        );

def change_settings_view(request, pk):
    if request.method == 'POST':
        form = CardSettingsForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('pasttrec_trb3setup:card', form.cleaned_data['card'].pk)
        else:
            return redirect('pasttrec_trb3setup:change_settings', pk)

    else:
        form = CardSettingsForm(instance=CardSettings.objects.get(pk=pk))
        return render(
            request,
            'pasttrec_trb3setup/card_settings.html',
            context = {
                'form' : form,
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
