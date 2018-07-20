from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views import generic
import json

from .models import Card, CardSettings, Connection, Revision, Setup, TDC
from .forms import CardConfigInsertForm, JsonUploadFileForm, RevisionForm
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

class CardView(generic.DetailView):
    model = Card
    template_name = 'pasttrec_trb3setup/card_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        card_id = self.kwargs.get('pk', None)

        cards = CardSettings.objects.filter(card=card_id).order_by('-revision__creation_on')

        context['revisions'] = cards

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

def import_select_view(request, setup):
    _setup = Setup.objects.get(pk=setup)
    _rev = Revision.objects.filter(setup__pk=setup).order_by('-creation_on')
    _form = RevisionForm(initial={'setup': setup})
    return render(
        request,
        'pasttrec_trb3setup/select_revision.html',
        context = {
            'setup' : _setup,
            'object_list' : _rev,
            'form' : _form
        }
    );

def import_insert_view(request, setup):
    _setup = Setup.objects.get(pk=setup)
    if request.method == 'POST':
        form = RevisionForm(request.POST)
        if form.is_valid():
            new_rev = form.save()

            return redirect('pasttrec_trb3setup:import_file', rev=new_rev.pk)

    return redirect('pasttrec_trb3setup:import_select_revision', setup=setup)

def build_list_of_names(d):
    l = []
    for k, v in d.items():
        for c in range(3):
            n = "name_{:s}_{:d}".format(k, c)
            l.append({ 'name' : n, 'sel': None, 'val' : v[c] })

    return l

def import_file_view(request, rev):
    _rev = Revision.objects.get(pk=rev)

    if request.method == 'POST':
        form = JsonUploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            d_str = b''
            for chunk in request.FILES['file'].chunks():
                d_str += chunk

            d = json.loads(d_str.decode())
            l = build_list_of_names(d)
            cards_form = CardConfigInsertForm(raw=d_str.decode(), extra=l)

            return render(
                request,
                'pasttrec_trb3setup/import_file.html',
                context = {
                    'setup' : _rev.setup,
                    'rev' : _rev,
                    'form_upload' : form,
                    'cards_form' : cards_form,
                    'cards' : { 'aaa' : 0 },
                }
            );
        else:
            return redirect('pasttrec_trb3setup:import_file', rev=_rev.pk)

    else:
        _form = JsonUploadFileForm()
        return render(
            request,
            'pasttrec_trb3setup/import_file.html',
            context = {
                'setup' : _rev.setup,
                'rev' : _rev,
                'form_upload' : _form,
            }
        );

def import_json_view(request, rev):
    _rev = Revision.objects.get(pk=rev)
    if request.method == 'POST':

        form = CardConfigInsertForm(request.POST)
        if form.is_valid():
            updated = []
            raw = request.POST['raw_data']
            d = json.loads(raw)
            l = build_list_of_names(d)

            for v in l:
                v['sel'] = request.POST[v['name']]
                if v['sel'] is not "":
                    obj, created = CardSettings.objects.update_or_create(
                        card=Card.objects.get(pk=v['sel']),
                        revision=_rev
                    )
                    data = v['val']
                    # asic #1
                    obj.bg_int_0 = data[0]['bg_int']
                    obj.gain_0 = data[0]['gain']
                    obj.peaking_0 = data[0]['peaking']
                    obj.tc1c_0 = data[0]['tc1c']
                    obj.tc1r_0 = data[0]['tc1r']
                    obj.tc2c_0 = data[0]['tc2c']
                    obj.tc2r_0 = data[0]['tc2r']

                    obj.threshold_0 = data[0]['vth']
                    obj.disabled_0 = False

                    obj.baseline_00 = data[0]['bl'][0]
                    obj.baseline_01 = data[0]['bl'][1]
                    obj.baseline_02 = data[0]['bl'][2]
                    obj.baseline_03 = data[0]['bl'][3]
                    obj.baseline_04 = data[0]['bl'][4]
                    obj.baseline_05 = data[0]['bl'][5]
                    obj.baseline_06 = data[0]['bl'][6]
                    obj.baseline_07 = data[0]['bl'][7]

                    obj.disabled_00 = False
                    obj.disabled_01 = False
                    obj.disabled_02 = False
                    obj.disabled_03 = False
                    obj.disabled_04 = False
                    obj.disabled_05 = False
                    obj.disabled_06 = False
                    obj.disabled_07 = False

                    # asic #2
                    obj.bg_int_1 = data[1]['bg_int']
                    obj.gain_1 = data[1]['gain']
                    obj.peaking_1 = data[1]['peaking']
                    obj.tc1c_1 = data[1]['tc1c']
                    obj.tc1r_1 = data[1]['tc1r']
                    obj.tc2c_1 = data[1]['tc2c']
                    obj.tc2r_1 = data[1]['tc2r']

                    obj.threshold_1 = data[1]['vth']
                    obj.disabled_1 = False

                    obj.baseline_10 = data[1]['bl'][0]
                    obj.baseline_11 = data[1]['bl'][1]
                    obj.baseline_12 = data[1]['bl'][2]
                    obj.baseline_13 = data[1]['bl'][3]
                    obj.baseline_14 = data[1]['bl'][4]
                    obj.baseline_15 = data[1]['bl'][5]
                    obj.baseline_16 = data[1]['bl'][6]
                    obj.baseline_17 = data[1]['bl'][7]

                    obj.disabled_10 = False
                    obj.disabled_11 = False
                    obj.disabled_12 = False
                    obj.disabled_13 = False
                    obj.disabled_14 = False
                    obj.disabled_15 = False
                    obj.disabled_16 = False
                    obj.disabled_17 = False

                    obj.save()
                    updated.append(obj.card)

            return render(
                request,
                'pasttrec_trb3setup/import_json.html',
                context = {
                    'setup' : _rev.setup,
                    'rev' : _rev,
                    'updated' : updated,
                }
            );

    return redirect('pasttrec_trb3setup:import_file', rev=_rev.pk)
