from confmodel.errors import ConfigError


class FieldFallback(object):
    required_fields = None

    def get_field_descriptor(self, config, field_name):
        field = config._fields.get(field_name, None)
        if field is None:
            raise ConfigError(
                "Undefined fallback field: '%s'" % (field_name,))
        return field

    def field_present(self, config, field_name):
        """
        Check if a value for the named field is present in the config data.

        :param config: :class:`.Config` instance containing config data.
        :param str field_name: Name of the field to look up.

        :returns:
            ``True`` if the value is present in the provided data, ``False``
            otherwise.
        """
        field = self.get_field_descriptor(config, field_name)
        return field.present(config)

    def present(self, config):
        if self.required_fields is None:
            raise NotImplementedError(
                "Please set .required_fields or override .present()")

        for field_name in self.required_fields:
            if not self.field_present(config, field_name):
                return False
        return True

    def build_value(self, config):
        raise NotImplementedError("Please implement .build_value()")


class SingleFieldFallback(FieldFallback):
    def __init__(self, field_name):
        self.field_name = field_name
        self.required_fields = [field_name]

    def build_value(self, config):
        return getattr(config, self.field_name)


class FormatStringFieldFallback(FieldFallback):
    def __init__(self, format_string, required_fields, optional_fields=()):
        self.format_string = format_string
        self.required_fields = required_fields
        self.optional_fields = optional_fields

    def build_value(self, config):
        field_values = {}
        for field_name in self.required_fields:
            field_values[field_name] = getattr(config, field_name)
        for field_name in self.optional_fields:
            field_values[field_name] = getattr(config, field_name)
        return self.format_string.format(**field_values)
