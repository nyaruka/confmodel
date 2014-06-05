import inspect
import textwrap

from confmodel.errors import ConfigError
from confmodel.fields import ConfigField
from confmodel.interfaces import IConfigData


def split_and_trim_docstring(docstring):
    lines = docstring.expandtabs().splitlines()
    if not lines:
        return []
    line_indents = set()
    # Examine the indentation of each line, skipping the first line because
    # it's special.
    for line in lines[1:]:
        stripped_line = line.lstrip()
        if stripped_line:
            # Skip empty lines.
            line_indents.add(len(line) - len(stripped_line))
    # Trim the indentation off each line. The first line is still special.
    trimmed_lines = [lines[0].strip()]
    if line_indents:
        indent_trim = min(line_indents)
        for line in lines[1:]:
            trimmed_lines.append(line[indent_trim:].rstrip())
    # Remove initial and final empty lines.
    while trimmed_lines and not trimmed_lines[0]:
        trimmed_lines.pop(0)
    while trimmed_lines and not trimmed_lines[-1]:
        trimmed_lines.pop()
    return trimmed_lines


def generate_doc(cls, fields, header_indent='', indent=' ' * 4):
    """
    Generate a docstring for a cls and its fields.
    """
    doc = split_and_trim_docstring(cls.__doc__ or '')
    doc.append("")
    doc.append("Configuration options:")
    for field in fields:
        header, field_doc = field.get_doc()
        doc.append("")
        doc.append(header_indent + header)
        doc.append("")
        doc.extend(textwrap.wrap(field_doc, initial_indent=indent,
                                 subsequent_indent=indent))
    return "\n".join(doc)


class ConfigMetaClass(type):
    def __new__(mcs, name, bases, class_dict):
        # locate Field instances
        fields = []
        unified_class_dict = {}
        for base in bases:
            unified_class_dict.update(inspect.getmembers(base))
        unified_class_dict.update(class_dict)

        for key, possible_field in unified_class_dict.items():
            if isinstance(possible_field, ConfigField):
                fields.append(possible_field)
                possible_field.setup(key)

        fields.sort(key=lambda f: f.creation_order)
        class_dict['_fields'] = dict((f.name, f) for f in fields)
        class_dict['_field_names'] = tuple(f.name for f in fields)
        cls = type.__new__(mcs, name, bases, class_dict)
        cls.__doc__ = generate_doc(cls, fields)
        return cls


class Config(object):
    """
    Config object.
    """

    __metaclass__ = ConfigMetaClass

    def __init__(self, config_data, static=False):
        self._config_data = IConfigData(config_data)
        self.static = static
        for field in self._get_fields():
            if self.static and not field.static:
                # Skip non-static fields on static configs.
                continue
            field.validate(self)
        self.post_validate()

    @classmethod
    def _get_fields(cls):
        return [cls._fields[field_name] for field_name in cls._field_names]

    def raise_config_error(self, message):
        """
        Raise a :exc:`.ConfigError` with the given message.
        """
        raise ConfigError(message)

    def post_validate(self):
        """
        Subclasses may override this to provide cross-field validation.

        Implementations should raise :exc:`.ConfigError` if the configuration
        is invalid (by calling :meth:`raise_config_error`, for example).
        """
        pass
