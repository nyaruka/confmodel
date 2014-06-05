from confmodel.config import FieldFallback


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
