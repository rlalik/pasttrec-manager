from django.contrib import admin
from django.urls import reverse, resolve

from .models import AsicBaselineSettings, AsicConfiguration, Card, CardCalibration, CardsSetup
from .querysets import queryset_for_card_field, queryset_for_admin_card_field

# Register your models here.


class CardAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["febid", "name", "notes"]}),
    ]
    # inlines = [CardSettingsInline]


class CardInline(admin.StackedInline):
    model = Card
    extra = 3
    show_change_link = True
    fields = ["febid", "name", "notes"]


admin.site.register(Card, CardAdmin)
admin.site.register(AsicConfiguration)
admin.site.register(AsicBaselineSettings)
admin.site.register(CardCalibration)
admin.site.register(CardsSetup)
