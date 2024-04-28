from django.contrib import admin
from django.urls import reverse, resolve

from .models import AsicBaselineSettings, AsicConfiguration, Card, CardCalibration
from .querysets import queryset_for_card_field, queryset_for_admin_card_field

# Register your models here.


# class AsicConfigurationAdmin(admin.ModelAdmin):
#     fieldsets = [(None, {"fields": ["name"]}), ("Extra info", {"fields": ["description"], "classes": ["collapse"]})]
#     list_display = ["name"]
# 
#     # inlines = [RevisionInline]


# class CardSettingsAdmin(admin.ModelAdmin):
#     fieldsets = [
#         (None, {"fields": ["card", "revision", "map_to"]}),
#         (
#             "Asic #1",
#             {
#                 "fields": [
#                     ("bg_int_0", "gain_0", "peaking_0", "tc1c_0", "tc1r_0", "tc2c_0", "tc2r_0"),
#                     ("threshold_0", "disabled_0"),
#                     ("baseline_00", "disabled_00"),
#                     ("baseline_01", "disabled_01"),
#                     ("baseline_02", "disabled_02"),
#                     ("baseline_03", "disabled_03"),
#                     ("baseline_04", "disabled_04"),
#                     ("baseline_05", "disabled_05"),
#                     ("baseline_06", "disabled_06"),
#                     ("baseline_07", "disabled_07"),
#                 ],
#                 "classes": ["collapse"],
#             },
#         ),
#         (
#             "Asic #2",
#             {
#                 "fields": [
#                     ("bg_int_1", "gain_1", "peaking_1", "tc1c_1", "tc1r_1", "tc2c_1", "tc2r_1"),
#                     ("threshold_1", "disabled_1"),
#                     ("baseline_10", "disabled_10"),
#                     ("baseline_11", "disabled_11"),
#                     ("baseline_12", "disabled_12"),
#                     ("baseline_13", "disabled_13"),
#                     ("baseline_14", "disabled_14"),
#                     ("baseline_15", "disabled_15"),
#                     ("baseline_16", "disabled_16"),
#                     ("baseline_17", "disabled_17"),
#                 ],
#                 "classes": ["collapse"],
#             },
#         ),
#     ]
#
#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if db_field.name == "map_to":
#             pk = resolve(request.path).kwargs.get("object_id", None)
#             if pk is not None:
#                 q = CardSettings.objects.get(pk=pk)
#                 kwargs["queryset"] = CardSettings.objects.filter(card=q.card)
#             else:
#                 kwargs["queryset"] = CardSettings.objects.none()
#         return super().formfield_for_foreignkey(db_field, request, **kwargs)


# class CardSettingsInline(admin.StackedInline):
#     model = CardSettings
#     extra = 0
#     fields = [
#         ("revision", "map_to"),
#         ("bg_int_0", "gain_0", "peaking_0", "tc1c_0", "tc1r_0", "tc2c_0", "tc2r_0"),
#         (
#             "threshold_0",
#             "baseline_00",
#             "baseline_01",
#             "baseline_02",
#             "baseline_03",
#             "baseline_04",
#             "baseline_05",
#             "baseline_06",
#             "baseline_07",
#         ),
#         (
#             "disabled_0",
#             "disabled_00",
#             "disabled_01",
#             "disabled_02",
#             "disabled_03",
#             "disabled_04",
#             "disabled_05",
#             "disabled_06",
#             "disabled_07",
#         ),
#         ("bg_int_1", "gain_1", "peaking_1", "tc1c_1", "tc1r_1", "tc2c_1", "tc2r_1"),
#         (
#             "threshold_1",
#             "baseline_10",
#             "baseline_11",
#             "baseline_12",
#             "baseline_13",
#             "baseline_14",
#             "baseline_15",
#             "baseline_16",
#             "baseline_17",
#         ),
#         (
#             "disabled_1",
#             "disabled_10",
#             "disabled_11",
#             "disabled_12",
#             "disabled_13",
#             "disabled_14",
#             "disabled_15",
#             "disabled_16",
#             "disabled_17",
#         ),
#     ]
#
#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         # if db_field.name == "map_to":
#         # pk = resolve(request.path).kwargs['object_id']
#         # if pk is not None:
#         # print(resolve(request.path), pk)
#         # q = CardSettings.objects.get(pk=pk)
#         # kwargs["queryset"] = CardSettings.objects.filter(card=q.card)
#         # else:
#         # kwargs["queryset"] = CardSettings.objects.none()
#         return super().formfield_for_foreignkey(db_field, request, **kwargs)


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


# admin.site.register(Configuration, ConfigurationAdmin)
# admin.site.register(Configuration)

admin.site.register(Card, CardAdmin)

admin.site.register(AsicConfiguration)
admin.site.register(AsicBaselineSettings)

admin.site.register(CardCalibration)

# admin.site.register(AsicConfigSettings, AsicConfigSettingsAdmin)
# admin.site.register(AsicBaselineSettings, AsicBaselineSettingsAdmin)
