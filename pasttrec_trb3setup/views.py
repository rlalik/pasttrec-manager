from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views import generic
import json

from .models import Card, CardSettings, Connection, Revision, Setup, TDC
from .exports import export_json
# Create your views here.

def create_revision_snapshot(revision):
    snapshot = {}

    result = Connection.objects.filter(
        revision__setup=revision.setup,
        revision__creation_on__lte=revision.creation_on)

    def find_last_card_revision(card, rev):
        if card is None:
            return None

        r = CardSettings.objects.filter(
            card=card.pk,
            revision__setup=rev.setup,
            revision__creation_on__lte=rev.creation_on
            ).order_by(
                '-revision__creation_on'
            )

        if len(r):
            return r.first()
        else:
            return None

    for r in result:
        tdc = r.tdc
        _c1 = r.card1
        _c2 = r.card2
        _c3 = r.card3

        c1 = find_last_card_revision(_c1, revision)
        c2 = find_last_card_revision(_c2, revision)
        c3 = find_last_card_revision(_c3, revision)

        ina = r.inactive

        ntdc = tdc.trbnetid

        if ina or (c1 is None and c2 is None and c3 is None):
            snapshot.pop(ntdc, None)
            continue

        if ntdc not in snapshot:
            snapshot[ntdc] = { 'pk': r.pk, 'name': ntdc, 'tdc': tdc, 'card1': None, 'card2': None, 'card3': None }

        snapshot[ntdc]['tdc'] = tdc
        snapshot[ntdc]['card1'] = c1
        snapshot[ntdc]['card2'] = c2
        snapshot[ntdc]['card3'] = c3

    return snapshot

class IndexView(generic.ListView):
    template_name = 'pasttrec_trb3setup/index.html'
    #context_object_name = 'trb3setups'

    def get_queryset(self):
        return Setup.objects.order_by('name')

class SetupView(generic.ListView):
    model = Setup
    template_name = 'pasttrec_trb3setup/setup.html'

    def get_queryset(self, **kwargs):
        setup_id = self.kwargs.get('setup_id', None)
        return Revision.objects.filter(setup__pk=setup_id).order_by('-creation_on')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        setup_id = self.kwargs.get('setup_id', None)
        context['setup'] = Setup.objects.get(pk=setup_id)
        return context

class RevisionView(generic.DetailView):
    model = Revision
    template_name = 'pasttrec_trb3setup/connection_revision_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        rev_id = self.kwargs.get('pk', None)
        revision = Revision.objects.get(pk=rev_id)

        context['setup'] = revision.setup

        revs = []
        current = None
        cres = Revision.objects.filter(setup__pk=revision.setup.pk).order_by('creation_on')
        for cr in cres:
            is_current = True if cr.pk is rev_id else False
            revs.append({ 'name' : cr.creation_on, 'pk' : cr.pk, 'active' : is_current })

            if is_current: current = cr

        context['revlist'] = revs

        snapshot = create_revision_snapshot(revision)

        s = []
        for k,v in snapshot.items():
            s.append(v)

        context['snapshot'] = s

        return context

def export_json_view(request, pk):
    revision = Revision.objects.get(pk=pk)
    snapshot = create_revision_snapshot(revision)
    s = export_json(snapshot)

    response = HttpResponse(json.dumps(s, indent=2), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename=export.json'
    return response
    #return JsonResponse(s)
    #return redirect('pasttrec_trb3setup:rev', pk=pk)
