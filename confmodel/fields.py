from copy import deepcopy
from urllib2 import urlparse
import re

from confmodel.errors import ConfigError


class ConfigField(object):
    """
    The base class for all config fields.

    A config field is a descriptor that reads a value from the source data,
    validates it, and transforms it into an appropriate Python object.

    :param str doc:
        Description of this field to be included in generated documentation.

    :param bool required:
        Set to ``True`` if this field is required, ``False`` if it is optional.
        Unless otherwise specified, fields are not required.

    :param default:
        The default value for this field if no value is provided. This is
        unused if the field is required.

    :param bool static:
        Set to ``True`` if this is a static field. See :ref:`static-field-docs`
        for further information.

    :param fallbacks:
        A list of :class:`FieldFallback` objects to try if the value isn't
        present in the source data. See :ref:`field-fallback-docs` for further
        information.

    Subclasses of :class:`ConfigField` are expected to override :meth:`clean`
    to convert values from the source data to the required form. :meth:`clean`
    is called during validation and also on every attribute access, so it
    should not perform expensive computation. (If expensive computation is
    necessary for some reason, the result should be cached.)

    There are two special attributes on this descriptor:

    .. attribute:: field_type = None

        A class attribute that specifies the field type in generated
        documentation. It should be a string, or ``None`` to indicate that the
        field type should remain unspecified.

    .. attribute:: name

        An instance attribute containing the name bound to this descriptor
        instance. It is set by metaclass magic when a :class:`.Config` subclass
        is defined.
    """
    _creation_order = 0

    field_type = None

    def __init__(self, doc, required=False, default=None, static=False,
                 fallbacks=()):
        # This hack is to allow us to track the order in which fields were
        # added to a config class. We want to do this so we can document fields
        # in the same order they're defined.
        self.creation_order = ConfigField._creation_order
        ConfigField._creation_order += 1
        self.name = None
        self.doc = doc
        self.required = required
        self.default = default
        self.static = static
        self.fallbacks = fallbacks

    def get_doc(self):
        """
        Build documentation for this field.

        A reST ``:param:`` field is generated based on the :attr:`name`,
        :attr:`doc`, and :attr:`field_type` attributes.

        :returns:
            A string containing a documentation section for this field.
        """
        if self.field_type is None:
            header = ":param %s:" % (self.name,)
        else:
            header = ":param %s %s:" % (self.field_type, self.name)
        return header, self.doc

    def setup(self, name):
        self.name = name

    def present(self, config, check_fallbacks=True):
        """
        Check if a value for this field is present in the config data.

        :param config:
            :class:`.Config` object containing config data.
        :param bool check_fallbacks:
            If ``False``, fallbacks will not be checked. (This is used
            internally to determine whether to use fallbacks when looking up
            data.)

        :returns:
            ``True`` if the value is present in the provided data, ``False``
            otherwise.
        """
        if self.name in config._config_data:
            return True
        if check_fallbacks:
            for fallback in self.fallbacks:
                if fallback.present(config):
                    return True
        return False

    def validate(self, config):
        """
        Check that the value is present if required and valid if present.

        If the field is required but no value is found, a :exc:`.ConfigError`
        is raised. Further validation is performed by calling :meth:`clean` and
        the value is assumed to be valid if no exceptions are raised.

        :param config:
            :class:`.Config` object containing config data.

        :returns:
            ``None``, but exceptions are raised for validation failures.
        """
        if self.required and not self.present(config):
            raise ConfigError(
                "Missing required config field '%s'" % (self.name,))
        # This will raise an exception if the value exists, but is invalid.
        self.get_value(config)

    def raise_config_error(self, message_suffix):
        """
        Raise a :exc:`.ConfigError` referencing this field.

        The text "Field '<field name>' <message suffix>" is used as the
        exception message.

        :param str message_suffix:
            A string to append to the exception message.

        :returns:
            Doesn't return, but raises a :exc:`.ConfigError`.
        """
        raise ConfigError("Field '%s' %s" % (self.name, message_suffix))

    def clean(self, value):
        """
        Clean and process a value from the source data.

        This should be overridden in subclasses to handle different kinds of
        fields.

        :param value:
            A value from the source data.

        :returns:
            A value suitable for Python code to use. This implementation merely
            returns the value it was given.
        """
        return value

    def find_value(self, config):
        """
        Find a value in the source data, fallbacks, or field default.

        :param config:
            :class:`.Config` object containing config data.

        :returns:
            The first value it finds.
        """
        if self.present(config, check_fallbacks=False):
            return config._config_data.get(self.name, self.default)
        for fallback in self.fallbacks:
            if fallback.present(config):
                return fallback.build_value(config)
        return self.default

    def get_value(self, config):
        """
        Get the cleaned value for this config field.

        This calls :meth:`find_value` to get the raw value and then calls
        :meth:`clean` to process it, unless the value is ``None``.

        This method may be overridden in subclasses if ``None`` needs to be
        handled differently.

        :param config:
            :class:`.Config` object containing config data.

        :returns:
            A cleaned value suitable for Python code to use.
        """
        value = self.find_value(config)
        return self.clean(value) if value is not None else None

    def __get__(self, config, cls):
        if config is None:
            return self
        if config.static and not self.static:
            self.raise_config_error("is not marked as static.")
        return self.get_value(config)

    def __set__(self, config, value):
        raise AttributeError("Config fields are read-only.")


class ConfigText(ConfigField):
    field_type = 'str'

    def clean(self, value):
        # XXX: We should really differentiate between "unicode" and "bytes".
        #      However, yaml.load() gives us bytestrings or unicode depending
        #      on the content.
        if not isinstance(value, basestring):
            self.raise_config_error("is not unicode.")
        return value


class ConfigInt(ConfigField):
    field_type = 'int'

    def clean(self, value):
        try:
            # We go via "str" to avoid silently truncating floats.
            # XXX: Is there a better way to do this?
            return int(str(value))
        except (ValueError, TypeError):
            self.raise_config_error("could not be converted to int.")


class ConfigFloat(ConfigField):
    field_type = 'float'

    def clean(self, value):
        try:
            return float(value)
        except (ValueError, TypeError):
            self.raise_config_error("could not be converted to float.")


class ConfigBool(ConfigField):
    field_type = 'bool'

    def clean(self, value):
        if isinstance(value, basestring):
            return value.strip().lower() not in ('false', '0', '')
        return bool(value)


class ConfigList(ConfigField):
    field_type = 'list'

    def clean(self, value):
        if isinstance(value, tuple):
            value = list(value)
        if not isinstance(value, list):
            self.raise_config_error("is not a list.")
        return deepcopy(value)


class ConfigDict(ConfigField):
    field_type = 'dict'

    def clean(self, value):
        if not isinstance(value, dict):
            self.raise_config_error("is not a dict.")
        return deepcopy(value)


class ConfigUrl(ConfigField):
    field_type = 'URL'

    def clean(self, value):
        if not isinstance(value, basestring):
            self.raise_config_error("is not a URL string.")
        # URLs must be bytes, not unicode.
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        return urlparse.urlparse(value)


class ConfigRegex(ConfigText):
    field_type = 'regex'

    def clean(self, value):
        value = super(ConfigRegex, self).clean(value)
        return re.compile(value)
