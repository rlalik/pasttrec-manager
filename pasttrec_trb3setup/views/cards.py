from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views import generic
import json, pasttrec

from ..models import Card, CardSettings, Connection, Revision, Setup, TDC
from ..forms import CardInsertForm
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
        form = CardInsertForm(request.POST)

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
        form = CardInsertForm()
        return render(
            request,
            'pasttrec_trb3setup/insert_cards.html',
            context = {
                'form' : form,
            }
        );
