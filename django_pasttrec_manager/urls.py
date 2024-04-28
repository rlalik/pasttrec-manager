from django.urls import path, re_path
from .views import *

app_name = "passtrec_trb3setup"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),

    path("configuration/<int:config_id>", views.AsicConfigurationView.as_view(), name="configuration"),

    path("cards", card.CardView.as_view(), name="cards"),
    path("card/<int:pk>", card.CardView.as_view(), name="card"),
    # path("card/<str:id>/c", card.card_view_lookup, name="card_by_id"),

    path("import/calibrations/wizard", wizards.JsonImportWizardView.as_view(), name="import_calibrations_wizard"),
    # path("card/import/insert", card.import_card_insert_view, name="import_card_insert"),

    path("calibration/<int:id>", calibration.CardCalibrationView.as_view(), name="calibration"),

    path("card/insert/<str:febid>/<str:name>", card.insert_card_view, name="insert_card"),
    path("card/insert", card.insert_card_view, name="insert_card"),
    path("card/multiple/<str:names>", card.insert_cards_view, name="insert_cards"),
    path("card/multiple", card.insert_cards_view, name="insert_cards"),
    # path("card/settings", card.add_settings_view, name="add_settings"),
    # path("card/settings/card/<int:card_pk>", card.add_settings_view, name="add_settings_by_card"),
    # path("card/settings/<int:card>", card.add_settings_view, name="add_settings_by_revision"),
    # path("card/settings/<int:card_pk>/<int:rev_pk>", card.add_settings_view, name="add_settings"),
    # path("card/settings/change/<int:pk>", card.change_settings_view, name="change_settings"),
    # path("card/settings/mass/<int:rev>", card.change_settings_mass_view, name="change_settings_mass"),
    # path("card/settings/delete/<int:card_pk>", card.delete_settings_view, name="delete_card_settings"),
    # path("export/json/<int:pk>", exports.export_json_view, name="export_json"),
    # path("export/shell/<int:pk>", exports.export_shell_view, name="export_shell"),
    # path("import/select/<int:setup>", exports.import_select_view, name="import_select_revision"),
    # path("import/insert/<int:setup>", exports.import_insert_view, name="import_insert_revision"),
    # path("import/file/<int:rev>", exports.import_file_view, name="import_file"),
    # path("import/<int:rev>", exports.import_json_view, name="import_json"),
]
