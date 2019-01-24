from django.forms.models import model_to_dict

import pasttrec

def dump_asic(card, a):
    asic = pasttrec.PasttrecRegs(
        bg_int = card.__dict__['bg_int_{:d}'.format(a)],
        gain = card.__dict__['gain_{:d}'.format(a)],
        peaking = card.__dict__['peaking_{:d}'.format(a)],
        tc1c = card.__dict__['tc1c_{:d}'.format(a)],
        tc1r = card.__dict__['tc1r_{:d}'.format(a)],
        tc2c = card.__dict__['tc2c_{:d}'.format(a)],
        tc2r = card.__dict__['tc2r_{:d}'.format(a)],
        vth = card.__dict__['threshold_{:d}'.format(a)],
    )

    for c in range(0,8):
        asic.bl[c] = card.__dict__['baseline_{:d}{:d}'.format(a, c)]

    return asic

def dump_card(card):
    asic1 = dump_asic(card, 0)
    asic2 = dump_asic(card, 1)

    c = pasttrec.PasttrecCard( card.card.name, asic1, asic2 )
    return c

def export_json(snapshot):
    d = []

    for k, v in snapshot.items():
        c1 = dump_card(v['card1']) if v['card1'] else None
        c2 = dump_card(v['card2']) if v['card2'] else None
        c3 = dump_card(v['card3']) if v['card3'] else None

        t = pasttrec.TdcConnection(k, c1, c2, c3)
        d.append(t)

    return d
