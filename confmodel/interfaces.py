from zope.interface import Interface, classImplements


class IConfigData(Interface):
    """
    Interface for a config data provider.

    This provides read-only access to some configuration data provider. The
    simplest implementation is a vanilla ``dict``.
    """

    def get(field_name, default):
        """
        Get the value of a config field.

        :param str field_name: The name of the field to look up.
        :param default: The value to return if the requested field is not
                        found.

        :returns: The value for the given ``field_name``, or ``default`` if
                  the field has not been specified.
        """

    def has_key(field_name):
        """
        Check for the existence of a config field.

        :param str field_name: The name of the field to look up.
        :returns: ``True`` if a value exists for the given ``field_name``,
                  ``False`` otherwise.
        """

    def __contains__(field_name):
        """
        Check for the existence of a config field.

        This is identical to :meth:`has_key` but is often more convenient to
        use.

        :param str field_name: The name of the field to look up.
        :returns: ``True`` if a value exists for the given ``field_name``,
                  ``False`` otherwise.
        """


# IConfigData is implemented by dict without any changes.
classImplements(dict, IConfigData)
