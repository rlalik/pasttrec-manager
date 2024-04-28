from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class AsicConfiguration(models.Model):
    name = models.CharField(max_length=255)
    notes = models.TextField(blank=True)

    bg_int = models.BooleanField(default=True)
    gain = models.IntegerField()
    peaking = models.IntegerField()
    tc1c = models.IntegerField()
    tc1r = models.IntegerField()
    tc2c = models.IntegerField()
    tc2r = models.IntegerField()

    threshold = models.IntegerField()
    disabled = models.BooleanField(default=False)

    def __hash__(self):
        return hash(
            (
                self.bg_int,
                self.gain,
                self.peaking,
                self.tc1c,
                self.tc1r,
                self.tc2c,
                self.tc2r,
                self.threshold,
            )
        )

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__hash__() == other.__hash__()

    def __str__(self):
        return (
            f"{self.name}: bg_int={self.bg_int} K={self.gain} Tp={self.peaking}"
            f" Tc1c={self.tc1c} Tc1r={self.tc1r}"
            f" Tc2c={self.tc2c} Tc1r={self.tc2r}"
        )

    def str_hash(self):
        return self.__str__().replace(" ", "_")

    def clean(self):
        e = {}
        if self.gain and not (0 <= self.gain <= 3):
            e["gain"] = _("Outside range 0-3")
        if self.peaking and not (0 <= self.peaking <= 3):
            e["peaking"] = _("Outside range 0-3")

        if self.tc1c and not (0 <= self.tc1c) <= 7:
            e["tc1c"] = _("Outside range 0-7")
        if self.tc1r and not (0 <= self.tc1r) <= 7:
            e["tc1r"] = _("Outside range 0-7")
        if self.tc2c and not (0 <= self.tc2c) <= 7:
            e["tc2c"] = _("Outside range 0-7")
        if self.tc2r and not (0 <= self.tc2r) <= 7:
            e["tc2r"] = _("Outside range 0-7")

        if self.threshold and not (0 <= self.threshold) <= 127:
            e["threshold"] = _("Outside range 0-127")

        if len(e):
            raise ValidationError(e)

    @classmethod
    def make_object(self, data):
        obj = self(
            bg_int=data["bg_int"],
            gain=data["gain"],
            peaking=data["peaking"],
            tc1c=data["tc1c"],
            tc1r=data["tc1r"],
            tc2c=data["tc2c"],
            tc2r=data["tc2r"],
            threshold=data["threshold"],
        )
        return obj

    @classmethod
    def create_from_values(self, data):
        obj = self(
            bg_int=data[0],
            gain=data[1],
            peaking=data[2],
            tc1c=data[3],
            tc1r=data[4],
            tc2c=data[5],
            tc2r=data[6],
            threshold=data[7],
        )
        return obj

    def find_same(self):
        obj = self(
            bg_int=data["bg_int"],
            gain=data["gain"],
            peaking=data["peaking"],
            tc1c=data["tc1c"],
            tc1r=data["tc1r"],
            tc2c=data["tc2c"],
            tc2r=data["tc2r"],
            threshold=data["threshold"],
        )
        return obj


class AsicBaselineSettings(models.Model):
    baseline_0 = models.IntegerField(default=0)
    baseline_1 = models.IntegerField(default=0)
    baseline_2 = models.IntegerField(default=0)
    baseline_3 = models.IntegerField(default=0)
    baseline_4 = models.IntegerField(default=0)
    baseline_5 = models.IntegerField(default=0)
    baseline_6 = models.IntegerField(default=0)
    baseline_7 = models.IntegerField(default=0)

    disabled_0 = models.BooleanField(default=False)
    disabled_1 = models.BooleanField(default=False)
    disabled_2 = models.BooleanField(default=False)
    disabled_3 = models.BooleanField(default=False)
    disabled_4 = models.BooleanField(default=False)
    disabled_5 = models.BooleanField(default=False)
    disabled_6 = models.BooleanField(default=False)
    disabled_7 = models.BooleanField(default=False)

    def __hash__(self):
        return hash(
            (
                self.baseline_0,
                self.baseline_1,
                self.baseline_2,
                self.baseline_3,
                self.baseline_4,
                self.baseline_5,
                self.baseline_6,
                self.baseline_7,
                self.disabled_0,
                self.disabled_1,
                self.disabled_2,
                self.disabled_3,
                self.disabled_4,
                self.disabled_5,
                self.disabled_6,
                self.disabled_7,
            )
        )

    def __str__(self):
        return (
            "_".join(
                [
                    str(x)
                    for x in (
                        self.baseline_0,
                        self.baseline_1,
                        self.baseline_2,
                        self.baseline_3,
                        self.baseline_4,
                        self.baseline_5,
                        self.baseline_6,
                        self.baseline_7,
                    )
                ]
            )
            + "__"
            + " ".join(
                [
                    str(x)
                    for x in (
                        self.disabled_0,
                        self.disabled_1,
                        self.disabled_2,
                        self.disabled_3,
                        self.disabled_4,
                        self.disabled_5,
                        self.disabled_6,
                        self.disabled_7,
                    )
                ]
            )
        )

    def clean(self):
        e = {}

        if self.baseline_0 and not (0 <= self.baseline_0 <= 31):
            e["baseline_0"] = _("Outside range 0-31")
        if self.baseline_1 and not (0 <= self.baseline_1 <= 31):
            e["baseline_1"] = _("Outside range 0-31")
        if self.baseline_2 and not (0 <= self.baseline_2 <= 31):
            e["baseline_2"] = _("Outside range 0-31")
        if self.baseline_3 and not (0 <= self.baseline_3 <= 31):
            e["baseline_3"] = _("Outside range 0-31")
        if self.baseline_4 and not (0 <= self.baseline_4 <= 31):
            e["baseline_4"] = _("Outside range 0-31")
        if self.baseline_5 and not (0 <= self.baseline_5 <= 31):
            e["baseline_5"] = _("Outside range 0-31")
        if self.baseline_6 and not (0 <= self.baseline_6 <= 31):
            e["baseline_6"] = _("Outside range 0-31")
        if self.baseline_7 and not (0 <= self.baseline_7 <= 31):
            e["baseline_7"] = _("Outside range 0-31")

        if len(e):
            raise ValidationError(e)

    @classmethod
    def make_object(self, data):
        obj = self(
            baseline_0=data[0],
            baseline_1=data[1],
            baseline_2=data[2],
            baseline_3=data[3],
            baseline_4=data[4],
            baseline_5=data[5],
            baseline_6=data[6],
            baseline_7=data[7],
        )
        return obj
