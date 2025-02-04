from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .forms import AddressAutoHiddenField as AddressAutoHiddenFormField
from .forms import LocationField as LocationFormField


def parse_location(location_string):
    """parse and convert coordinates from string to tuple"""
    args = location_string.split(",")
    if len(args) != 2:
        raise ValidationError(_("Invalid input for a Location instance"))

    lat = args[0]
    lng = args[1]

    try:
        lat = float(lat)
    except ValueError:
        raise ValidationError(_("Invalid input for a Location instance. Latitude must be convertible to float "))
    try:
        lng = float(lng)
    except ValueError:
        raise ValidationError(_("Invalid input for a Location instance. Longitude must be convertible to float "))

    return lat, lng


class LocationField(models.CharField):
    """custom model field for storing location"""

    description = _("Location field (latitude and longitude).")

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 63
        self.map_attrs = kwargs.pop("map_attrs", {})
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        kwargs["map_attrs"] = self.map_attrs
        return name, path, args, kwargs

    def from_db_value(self, value, expression=None, connection=None):
        if value is None:
            return value
        return parse_location(value)

    def to_python(self, value):
        if isinstance(value, tuple):
            return value

        if value is None:
            return value

        return parse_location(value)

    def get_prep_value(self, value):
        if value is None:
            return value

        return "{},{}".format(value[0], value[1])

    def formfield(self, **kwargs):
        defaults = {'form_class': LocationFormField}
        defaults.update(kwargs)
        defaults.update({"map_attrs": self.map_attrs})
        return super().formfield(**defaults)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)


class AddressAutoHiddenField(models.TextField):
    """custom model field for storing address"""
    description = _("Address field which automatically fill with address from LocationField.")

    def formfield(self, **kwargs):
        defaults = {'form_class': AddressAutoHiddenFormField}
        defaults.update(kwargs)
        return models.Field.formfield(self, **defaults)
