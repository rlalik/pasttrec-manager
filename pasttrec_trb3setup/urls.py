from django.urls import path, re_path

app_name = 'passtrec_trb3setup'

from .views import *

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('setup/<int:setup_id>', views.SetupView.as_view(), name='setup'),
    path('rev/<int:pk>', views.RevisionView.as_view(), name='rev'),
    path('rev/add/<int:setup_id>', views.revision_add_view, name='rev_add'),

    path('card/<int:pk>', cards.CardView.as_view(), name='card'),
    path('card/insert', cards.insert_card_view, name='insert_card'),
    path('card/multiple', cards.insert_cards_view, name='insert_cards'),

    path('card/settings', cards.add_settings_view, name='add_settings'),
    path('card/settings/card/<int:card>', cards.add_settings_view, name='add_settings_by_card'),
    path('card/settings/<int:card>', cards.add_settings_view, name='add_settings_by_revision'),
    path('card/settings/<int:card>/<int:rev>', cards.add_settings_view, name='add_settings'),

    path('card/settings/change/<int:pk>', cards.change_settings_view, name='change_settings'),
    path('card/settings/mass/<int:rev>', cards.change_settings_mass_view, name='change_settings_mass'),

    path('connection/add', connections.add_connection_view, name='add_connection'),
    path('connection/add/rev/<int:rev>', connections.add_connection_view, name='add_connection_by_rev'),
    path('connection/add/tdc/<int:tdc>', connections.add_connection_view, name='add_connection_by_tdc'),
    path('connection/add/<int:rev>/<int:tdc>', connections.add_connection_view, name='add_connection'),
    path('connection/change/<int:pk>', connections.edit_connection_view, name='change_connection'),

    path('export/json/<int:pk>', exports.export_json_view, name='export_json'),
    path('import/select/<int:setup>', exports.import_select_view, name='import_select_revision'),
    path('import/insert/<int:setup>', exports.import_insert_view, name='import_insert_revision'),
    path('import/file/<int:rev>', exports.import_file_view, name='import_file'),
    path('import/<int:rev>', exports.import_json_view, name='import_json'),
]
