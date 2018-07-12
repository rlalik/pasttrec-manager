from django.urls import path

app_name = 'passtrec_trb3setup'

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('setup/<int:setup_id>', views.SetupView.as_view(), name='setup'),
    path('rev/<int:pk>', views.RevisionView.as_view(), name='rev'),
]

