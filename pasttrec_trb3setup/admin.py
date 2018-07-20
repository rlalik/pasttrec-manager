from django.contrib import admin
from django.urls import reverse, resolve

from .models import Card, CardSettings, Connection, Revision, Setup, TDC

# extra functions

def queryset_for_card_field(field, request, **kwargs):
    resolved = resolve(request.path)

    if resolved.url_name == 'pasttrec_trb3setup_revision_add':
        return Card.objects.none()

    if resolved.url_name == 'pasttrec_trb3setup_revision_change':
        obj_id = resolved.kwargs['object_id']
        if obj_id is not None:
            q = Revision.objects.get(pk=obj_id)
            q2 = Card.objects.filter(
                cardsettings__revision__setup=q.setup.pk,
                cardsettings__revision__creation_on__lte=q.creation_on
            ).distinct()
            return q2
        else:
            return Card.objects.none()

    if resolved.url_name == 'pasttrec_trb3setup_connection_add':
        return Card.objects.none()

    if resolved.url_name == 'pasttrec_trb3setup_connection_change':
        obj_id = resolved.kwargs['object_id']
        if obj_id is not None:
            q = Connection.objects.get(pk=obj_id)
            q2 = Card.objects.filter(
                cardsettings__revision__setup=q.revision.setup.pk,
                cardsettings__revision__creation_on__lte=q.revision.creation_on
            ).distinct()
            return q2
        else:
            return Card.objects.none()

    return Card.objects.none()

# Register your models here.

class ConnectionInline(admin.StackedInline):
    model = Connection
    extra = 3
    show_change_link = True
    fields = [ ('revision', 'tdc', 'card1', 'card2', 'card3', 'inactive') ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in [ "card1", "card2", "card3" ]:
            kwargs["queryset"] = queryset_for_card_field(
                db_field.name, request, **kwargs)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

##class SetupRevisionAdmin(admin.ModelAdmin):
    ##model = SetupRevision
    ##extra = 1
    ##show_change_link = True
    ##fields = [ 'setup', 'revision' ]

    ##inlines = [ConnectionInline]

#class SetupRevisionInline(admin.StackedInline):
    #model = SetupRevision
    #extra = 1
    #show_change_link = True
    #fields = [ 'setup', 'revision' ]


class RevisionAdmin(admin.ModelAdmin):
    model = Revision
    extra = 1
    show_change_link = True
    fields = [ 'setup', 'creation_on' ]

    inlines = [ConnectionInline]

class RevisionInline(admin.StackedInline):
    model = Revision
    extra = 1
    show_change_link = True
    fields = [ 'setup', 'creation_on' ]


class SetupAdmin(admin.ModelAdmin):
    fieldsets = [
        ( None,         { 'fields' : ['name'] }),
        ( 'Extra info', { 'fields' : ['description'], 'classes': ['collapse'] })
    ]
    list_display = [ 'name' ]

    inlines = [RevisionInline]

class ConnectionAdmin(admin.ModelAdmin):
    fieldsets = [
        ( None,         { 'fields' : ['revision', 'tdc', 'card1', 'card2', 'card3', 'inactive'] }),
        ( 'Extra info', { 'fields' : ['notes'], 'classes': ['collapse'] })
    ]

    list_display = [ 'revision', 'tdc', 'card1', 'card2', 'card3', 'inactive' ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in [ "card1", "card2", "card3" ]:
            kwargs["queryset"] = queryset_for_card_field(
                db_field.name, request, **kwargs)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class CardSettingsAdmin(admin.ModelAdmin):
    fieldsets = [
        ( None,         { 'fields' : ['card', 'revision', 'map_to'] }),
        ( 'Asic #1',    { 'fields' : [
            ('bg_int_0', 'gain_0', 'peaking_0', 'tc1c_0', 'tc1r_0', 'tc2c_0', 'tc2r_0' ),
            ('threshold_0', 'disabled_0'),
            ('baseline_00', 'disabled_00' ),
            ('baseline_01', 'disabled_01' ),
            ('baseline_02', 'disabled_02' ),
            ('baseline_03', 'disabled_03' ),
            ('baseline_04', 'disabled_04' ),
            ('baseline_05', 'disabled_05' ),
            ('baseline_06', 'disabled_06' ),
            ('baseline_07', 'disabled_07' ),
        ], 'classes': ['collapse'] } ),
        ( 'Asic #2',    { 'fields' : [
            ('bg_int_1', 'gain_1', 'peaking_1', 'tc1c_1', 'tc1r_1', 'tc2c_1', 'tc2r_1' ),
            ('threshold_1', 'disabled_1'),
            ('baseline_10', 'disabled_10' ),
            ('baseline_11', 'disabled_11' ),
            ('baseline_12', 'disabled_12' ),
            ('baseline_13', 'disabled_13' ),
            ('baseline_14', 'disabled_14' ),
            ('baseline_15', 'disabled_15' ),
            ('baseline_16', 'disabled_16' ),
            ('baseline_17', 'disabled_17' ),
        ], 'classes': ['collapse'] } )
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "map_to":
            pk = resolve(request.path).kwargs.get('object_id', None)
            if pk is not None:
                q = CardSettings.objects.get(pk=pk)
                kwargs["queryset"] = CardSettings.objects.filter(card=q.card)
            else:
                kwargs["queryset"] = CardSettings.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class CardSettingsInline(admin.StackedInline):
    model = CardSettings
    extra = 0
    fields = [ ('revision', 'map_to'),
               ('bg_int_0', 'gain_0', 'peaking_0', 'tc1c_0', 'tc1r_0', 'tc2c_0', 'tc2r_0' ),
               ('threshold_0',
                'baseline_00', 'baseline_01', 'baseline_02', 'baseline_03',
                'baseline_04', 'baseline_05', 'baseline_06', 'baseline_07'),
               ('disabled_0',
                'disabled_00', 'disabled_01', 'disabled_02', 'disabled_03',
                'disabled_04', 'disabled_05', 'disabled_06', 'disabled_07'),
               ('bg_int_1', 'gain_1', 'peaking_1', 'tc1c_1', 'tc1r_1', 'tc2c_1', 'tc2r_1' ),
               ('threshold_1',
                'baseline_10', 'baseline_11', 'baseline_12', 'baseline_13',
                'baseline_14', 'baseline_15', 'baseline_16', 'baseline_17'),
               ('disabled_1',
                'disabled_10', 'disabled_11', 'disabled_12', 'disabled_13',
                'disabled_14', 'disabled_15', 'disabled_16', 'disabled_17')
            ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        #if db_field.name == "map_to":
            #pk = resolve(request.path).kwargs['object_id']
            #if pk is not None:
                #print(resolve(request.path), pk)
                #q = CardSettings.objects.get(pk=pk)
                #kwargs["queryset"] = CardSettings.objects.filter(card=q.card)
            #else:
                #kwargs["queryset"] = CardSettings.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class CardAdmin(admin.ModelAdmin):
    fieldsets = [
        ( None,         { 'fields' : ['name', 'notes'] }),
    ]
    inlines = [CardSettingsInline]

class CardInline(admin.StackedInline):
    model = Card
    extra = 3
    show_change_link = True
    fields = [ 'name', 'notes' ]

admin.site.register(Setup, SetupAdmin)
admin.site.register(TDC)

admin.site.register(Connection, ConnectionAdmin)
#admin.site.register(SetupRevision, SetupRevisionAdmin)

admin.site.register(Card, CardAdmin)
admin.site.register(CardSettings, CardSettingsAdmin)

admin.site.register(Revision, RevisionAdmin)
