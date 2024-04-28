from django.views import generic

from ..models import CardCalibration


class CardCalibrationView(generic.DetailView):
    model = CardCalibration()
    template_name = "django_pasttrec_manager/card_calibration_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        card_id = self.kwargs.get("pk", None)

        calibrations = CardCalibration.objects.filter(card=card_id)

        context["calibrations"] = calibrations

        return context
