from django.forms.models import model_to_dict

def dump_card(card):
    def get_dict() :
        return {
        'bg_int' : 0, 'K' : 0, 'Tp' : 0,
        'TC1C' : 0, 'TC1R' : 0, 'TC2C' : 0, 'TC2R' : 0,
        'threshold' : 0, 'disabled' : False,
        'baselines' : [ 0 ] * 8,
        'disables' : [ False ] * 8
        }

    d = [ get_dict() for i in range(0,2) ]

    for a in range(0,2):
        d[a]['threshold'] = card.__dict__['threshold_{:d}'.format(a)]
        d[a]['disabled'] = card.__dict__['disabled_{:d}'.format(a)]

        for c in range(0,8):
            d[a]['baselines'][c] = card.__dict__['baseline_{:d}{:d}'.format(a, c)]
            d[a]['disables'][c] = card.__dict__['disabled_{:d}{:d}'.format(a, c)]

    return d

def export_json(snapshot):
    d = {}
    for k, v in snapshot.items():
        d[k] = {}

        if 'card1' in v:
            d[k]['card1'] = dump_card(v['card1'])
        if 'card2' in v:
            d[k]['card2'] = dump_card(v['card2'])
        if 'card3' in v:
            d[k]['card3'] = dump_card(v['card3'])

    return d
