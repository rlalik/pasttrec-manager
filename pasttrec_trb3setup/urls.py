from django.urls import path

app_name = 'passtrec_trb3setup'

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('setup/<int:setup_id>', views.SetupView.as_view(), name='setup'),
    path('rev/<int:pk>', views.RevisionView.as_view(), name='rev'),
    path('card/<int:pk>', views.CardView.as_view(), name='card'),
    path('export/json/<int:pk>', views.export_json_view, name='export_json'),
    path('import/select/<int:setup>', views.import_select_view, name='import_select_revision'),
    path('import/insert/<int:setup>', views.import_insert_view, name='import_insert_revision'),
    path('import/file/<int:rev>', views.import_file_view, name='import_file'),
    path('import/<int:rev>', views.import_json_view, name='import_json'),
]
