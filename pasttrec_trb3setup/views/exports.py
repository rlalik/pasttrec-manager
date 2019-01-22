from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views import generic
import json, pasttrec

from ..models import Card, CardSettings, Connection, Revision, Setup, TDC
from ..forms import CardConfigInsertForm, JsonUploadFileForm, RevisionForm
from ..exports import export_json
from .views import create_revision_snapshot
# Create your views here.

def export_json_view(request, pk):
    revision = Revision.objects.get(pk=pk)
    snapshot = create_revision_snapshot(revision)
    s = export_json(snapshot)

    response = HttpResponse(json.dumps(pasttrec.dump(s), indent=2), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename=export.json'
    return response
    #return JsonResponse(s)
    #return redirect('pasttrec_trb3setup:rev', pk=pk)

def export_shell_view(request, pk):
    revision = Revision.objects.get(pk=pk)
    snapshot = create_revision_snapshot(revision)
    s = export_json(snapshot)

    response = HttpResponse('\n'.join(pasttrec.dump_script(s)), content_type='text/x-shellscript')
    response['Content-Disposition'] = 'attachment; filename=export.sh'
    return response

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
        if k == 'version': continue

        for c in range(1,4):
            n = "name_{:s}_{:d}".format(k, c)
            l.append({ 'name' : n, 'sel': None, 'val' : v['cable{:d}'.format(c)] })

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
            res1, res2 = pasttrec.load(d)
            if res1 == False:
                return render(
                    request,
                    'pasttrec_trb3setup/import_file.html',
                    context = {
                        'setup' : _rev.setup,
                        'rev' : _rev,
                        'form_upload' : form,
                        'version_error' : res2,
                        'version_current' : pasttrec.LIBVERSION
                    }
                );

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
                    obj.bg_int_0 = data['asic1']['bg_int']
                    obj.gain_0 = data['asic1']['gain']
                    obj.peaking_0 = data['asic1']['peaking']
                    obj.tc1c_0 = data['asic1']['tc1c']
                    obj.tc1r_0 = data['asic1']['tc1r']
                    obj.tc2c_0 = data['asic1']['tc2c']
                    obj.tc2r_0 = data['asic1']['tc2r']

                    obj.threshold_0 = data['asic1']['vth']
                    obj.disabled_0 = False

                    obj.baseline_00 = data['asic1']['bl'][0]
                    obj.baseline_01 = data['asic1']['bl'][1]
                    obj.baseline_02 = data['asic1']['bl'][2]
                    obj.baseline_03 = data['asic1']['bl'][3]
                    obj.baseline_04 = data['asic1']['bl'][4]
                    obj.baseline_05 = data['asic1']['bl'][5]
                    obj.baseline_06 = data['asic1']['bl'][6]
                    obj.baseline_07 = data['asic1']['bl'][7]

                    obj.disabled_00 = False
                    obj.disabled_01 = False
                    obj.disabled_02 = False
                    obj.disabled_03 = False
                    obj.disabled_04 = False
                    obj.disabled_05 = False
                    obj.disabled_06 = False
                    obj.disabled_07 = False

                    # asic #2
                    obj.bg_int_1 = data['asic2']['bg_int']
                    obj.gain_1 = data['asic2']['gain']
                    obj.peaking_1 = data['asic2']['peaking']
                    obj.tc1c_1 = data['asic2']['tc1c']
                    obj.tc1r_1 = data['asic2']['tc1r']
                    obj.tc2c_1 = data['asic2']['tc2c']
                    obj.tc2r_1 = data['asic2']['tc2r']

                    obj.threshold_1 = data['asic2']['vth']
                    obj.disabled_1 = False

                    obj.baseline_10 = data['asic2']['bl'][0]
                    obj.baseline_11 = data['asic2']['bl'][1]
                    obj.baseline_12 = data['asic2']['bl'][2]
                    obj.baseline_13 = data['asic2']['bl'][3]
                    obj.baseline_14 = data['asic2']['bl'][4]
                    obj.baseline_15 = data['asic2']['bl'][5]
                    obj.baseline_16 = data['asic2']['bl'][6]
                    obj.baseline_17 = data['asic2']['bl'][7]

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
