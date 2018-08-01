from django.urls import path

app_name = 'passtrec_trb3setup'

from .views import *

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('setup/<int:setup_id>', views.SetupView.as_view(), name='setup'),
    path('rev/<int:pk>', views.RevisionView.as_view(), name='rev'),

    path('card/<int:pk>', cards.CardView.as_view(), name='card'),
    path('card/insert', cards.insert_card_view, name='insert_card'),
    path('card/multiple', cards.insert_cards_view, name='insert_cards'),

    path('export/json/<int:pk>', exports.export_json_view, name='export_json'),
    path('import/select/<int:setup>', exports.import_select_view, name='import_select_revision'),
    path('import/insert/<int:setup>', exports.import_insert_view, name='import_insert_revision'),
    path('import/file/<int:rev>', exports.import_file_view, name='import_file'),
    path('import/<int:rev>', exports.import_json_view, name='import_json'),
]
