from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views import generic
import json, pasttrec
from enum import Enum

from ..models import Card, CardSettings, Connection, Revision, Setup, TDC
# Create your views here.

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

def create_revision_snapshot(revision):
    snapshot = {}

    result = Connection.objects.filter(
            revision__setup=revision.setup,
            revision__creation_on__lte=revision.creation_on
        )

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
            snapshot[ntdc] = { 'pk': r, 'name': ntdc, 'tdc': tdc, 'card1': None, 'card2': None, 'card3': None }

        snapshot[ntdc]['r'] = r
        snapshot[ntdc]['tdc'] = tdc
        snapshot[ntdc]['card1'] = c1
        snapshot[ntdc]['card2'] = c2
        snapshot[ntdc]['card3'] = c3

    return snapshot

class State():
    NONE = 0        # no action before
    ADDED = 1       # card added to connection
    CHANGED = 2     # card replaced
    UPDATED = 3     # card settings changed
    CHANGED_AND_UPDATED = 4 # card changed and settings changd, not used now
    REMOVED = 5     # card removed
    KEPT = 6        # keep from previous revision

def get_map_dict():
    return {
        'tdc' : None,
        'rev' : None,
        'status' : State.NONE,
        'card1' : None,
        'card1_s' : State.NONE,
        'card2' : None,
        'card2_s' : State.NONE,
        'card3' : None,
        'card3_s' : State.NONE,
    }

def create_revisions_map(setup):
    def set_status(prev, curr):
        if curr is None:
            if prev is None:
                # keep the same
                return 0, State.NONE
            else:
                # removed
                return 1, State.REMOVED

        if prev is None:
            # new, added
            return 1, State.ADDED

        if prev != curr:
            # changed or updated
            if prev.card != curr.card:
                return 1, State.CHANGED 
            else:
                return 2, State.UPDATED
        else:
            # keep the same
            return 0, State.KEPT

    map = {}

    revs = Revision.objects.filter(
            setup=setup
        ).order_by(
            'creation_on'
        )
    nrevs = len(revs)

    cons = Connection.objects.filter(
            revision__setup=setup
        )
    ncons = len(cons)

    for c in cons:
        tdc = c.tdc.trbnetid
        if tdc not in map:
            map[tdc] = [ get_map_dict() for _ in range(nrevs) ]

    for _r in range(nrevs):
        # get connetion
        cons = Connection.objects.filter(
            revision=revs[_r]
        )

        for c in cons:
            _tdc = c.tdc
            tdc = _tdc.trbnetid

            rev = c.revision
            _c1 = c.card1
            _c2 = c.card2
            _c3 = c.card3
            ina = c.inactive

            if ina or (_c1 is None and _c2 is None and _c3 is None):
                map[tdc][_r]['status'] = State.REMOVED
                continue

            map[tdc][_r]['tdc'] = _tdc
            if _r == 0:
                c1 = find_last_card_revision(_c1, rev)
                c2 = find_last_card_revision(_c2, rev)
                c3 = find_last_card_revision(_c3, rev)

                map[tdc][0]['card1'] = c1
                map[tdc][0]['card2'] = c2
                map[tdc][0]['card3'] = c3

                map[tdc][0]['status'] = State.ADDED
                map[tdc][0]['card1_s'] = State.ADDED if c1 else State.NONE
                map[tdc][0]['card2_s'] = State.ADDED if c2 else State.NONE
                map[tdc][0]['card3_s'] = State.ADDED if c3 else State.NONE
                map[tdc][0]['rev'] = revs[0]
            else:
                map[tdc][_r]['status'] = State.CHANGED
                map[tdc][_r]['card1'] = _c1
                map[tdc][_r]['card2'] = _c2
                map[tdc][_r]['card3'] = _c3

        cards = CardSettings.objects.filter(
            revision=revs[_r]
        )

    for k, v in map.items():
        for _r in range(1, nrevs):
            
            # status in previous revision
            status_prev = v[_r-1]['status']
            c1_prev = v[_r-1]['card1']
            c1s_prev = v[_r-1]['card1_s']
            c2_prev = v[_r-1]['card2']
            c2s_prev = v[_r-1]['card2_s']
            c3_prev = v[_r-1]['card3']
            c3s_prev = v[_r-1]['card3_s']

            status_curr = v[_r]['status']
            _c1_curr = v[_r]['card1']
            _c2_curr = v[_r]['card2']
            _c3_curr = v[_r]['card3']

            map[k][_r]['rev'] = revs[_r]

            # if got inactive/cards removed

            if status_curr == State.NONE and status_prev != State.REMOVED  and status_prev != State.NONE:
                #c1_curr = c1_prev
                #c2_curr = c2_prev
                #c3_curr = c3_prev
                c1_curr = find_last_card_revision(c1_prev.card, revs[_r]) if c1_prev else None
                c2_curr = find_last_card_revision(c2_prev.card, revs[_r]) if c2_prev else None
                c3_curr = find_last_card_revision(c3_prev.card, revs[_r]) if c3_prev else None
            else:
                c1_curr = find_last_card_revision(_c1_curr, revs[_r])
                c2_curr = find_last_card_revision(_c2_curr, revs[_r])
                c3_curr = find_last_card_revision(_c3_curr, revs[_r])

            v[_r]['card1'] = c1_curr
            v[_r]['card2'] = c2_curr
            v[_r]['card3'] = c3_curr

            has_change = 0x0
            hc = False
            hc, v[_r]['card1_s'] = set_status(c1_prev, c1_curr)
            has_change |= hc

            hc, v[_r]['card2_s'] = set_status(c2_prev, c2_curr)
            has_change |= hc

            hc, v[_r]['card3_s'] = set_status(c3_prev, c3_curr)
            has_change |= hc

            if has_change:
                v[_r]['status'] = State.CHANGED if has_change & 1 else State.UPDATED
            else:
                v[_r]['status'] = State.KEPT if status_prev != State.NONE else State.NONE

    return map

class IndexView(generic.ListView):
    template_name = 'pasttrec_trb3setup/index.html'
    #context_object_name = 'trb3setups'

    def get_queryset(self):
        return None
        return Setup.objects.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        setup_id = self.kwargs.get('setup_id', None)
        context['setups'] = Setup.objects.order_by('name')
        context['cards'] = Card.objects.order_by('name')
        return context

class SetupView(generic.ListView):
    model = Setup
    template_name = 'pasttrec_trb3setup/setup.html'

    def get_queryset(self, **kwargs):
        setup_id = self.kwargs.get('setup_id', None)
        return Revision.objects.filter(setup__pk=setup_id).order_by('-creation_on')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        setup_id = self.kwargs.get('setup_id', None)
        setup = Setup.objects.get(pk=setup_id)
        context['setup'] = setup

        map = create_revisions_map(setup)
        context['map'] = map
        context['State'] = State

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
