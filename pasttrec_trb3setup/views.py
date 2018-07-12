from django.shortcuts import render
from django.views import generic

from .models import Card, CardSettings, Connection, Revision, Setup, TDC
# Create your views here.

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
        cres = Revision.objects.filter(setup__pk=1).order_by('creation_on')
        for cr in cres:
            is_current = True if cr.pk is rev_id else False
            revs.append({ 'name' : cr.creation_on, 'pk' : cr.pk, 'active' : is_current })

            if is_current: current = cr

        context['revlist'] = revs


        status = {}
        result = Connection.objects.filter(
            revision__setup=revision.setup,
            revision__creation_on__lte=current.creation_on)

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
                status.pop(ntdc, None)
                continue

            if ntdc not in status:
                status[ntdc] = { 'pk': r.pk, 'name': ntdc, 'tdc': tdc, 'card1': None, 'card2': None, 'card3': None }

            status[ntdc]['tdc'] = tdc
            status[ntdc]['card1'] = c1
            status[ntdc]['card2'] = c2
            status[ntdc]['card3'] = c3

        s = []
        for k,v in status.items():
            s.append(v)

        context['status'] = s

        return context
