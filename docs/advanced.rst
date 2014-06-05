=================
Advanced features
=================


.. _field-fallback-docs:

Field fallbacks
===============

Sometimes it's necessary for a config field to refer to other fields to find or
construct its value, particularly as systems evolve over time. This is managed
in a flexible way using :class:`.FieldFallback` objects.


.. testcode:: fallbacks1

   from confmodel.config import Config, ConfigText, SingleFieldFallback

   class SimpleFallbackConfig(Config):
       """
       This config specification demonstrates the use of a SingleFieldFallback.
       """

       incantation = ConfigText(
           "The incantation to recite. (Falls back to the 'magic_word' field.)",
           required=True, fallbacks=[SingleFieldFallback("magic_word")])
       magic_word = ConfigText("*DEPRECATED* The magic word to utter.")


The above specification requires the ``incantation`` field, but of that's not
present the ``magic_word`` field will be used instead. Validation will fail if
neither is present.


.. doctest:: fallbacks1

   >>> SimpleFallbackConfig({u'incantation': u'foo'}).incantation
   u'foo'
   >>> SimpleFallbackConfig({u'magic_word': u'please'}).incantation
   u'please'
   >>> SimpleFallbackConfig({}).incantation
   Traceback (most recent call last):
       ...
   ConfigError: Missing required config field 'incantation'


A field used as a fallback is still a normal field in every way.


.. doctest:: fallbacks1

   >>> print SimpleFallbackConfig({u'incantation': u'foo'}).magic_word
   None
   >>> SimpleFallbackConfig({u'magic_word': u'please'}).magic_word
   u'please'


Multiple fallbacks
------------------

Multiple fallbacks may be used for a single field by listing then in order of
preference.


.. doctest:: fallbacks2

   >>> from confmodel.config import Config, ConfigText, SingleFieldFallback
   >>> class MultiFallbackConfig(Config):
   ...     """
   ...     This config specification demonstrates the use of multiple fallbacks.
   ...     """
   ...     incantation = ConfigText(
   ...         "The incantation to recite."
   ...         " (Falls back to the 'magic_word' and 'galdr' fields.)",
   ...         required=True, fallbacks=[
   ...             SingleFieldFallback("magic_word"),
   ...             SingleFieldFallback("galdr"),
   ...         ])
   ...     magic_word = ConfigText("*DEPRECATED* The magic word to utter.")
   ...     galdr = ConfigText("*DEPRECATED* Runes to chant.")

   >>> MultiFallbackConfig({u'incantation': u'foo'}).incantation
   u'foo'
   >>> MultiFallbackConfig({u'magic_word': u'please'}).incantation
   u'please'
   >>> MultiFallbackConfig({u'galdr': u'heyri jotnar'}).incantation
   u'heyri jotnar'
   >>> MultiFallbackConfig({
   ...     u'magic_word': u'please',
   ...     u'galdr': u'heyri jotnar',
   ... }).incantation
   u'please'
   >>> MultiFallbackConfig({}).incantation
   Traceback (most recent call last):
       ...
   ConfigError: Missing required config field 'incantation'


Fallbacks with defaults
-----------------------

Default values for fallbacks are ignored [#fallback-default]_ and the field's
default value is used as a last resort if no fallback values are found.


.. doctest:: fallbacks3

   >>> from confmodel.config import Config, ConfigText, SingleFieldFallback
   >>> class FallbackDefaultsConfig(Config):
   ...     """
   ...     This config specification demonstrates fallbacks with defaults.
   ...     """
   ...     incantation = ConfigText(
   ...         "The incantation to recite. (Falls back to the 'magic_word' field.)",
   ...        default=u"xyzzy", fallbacks=[SingleFieldFallback("magic_word")])
   ...     magic_word = ConfigText(
   ...         "*DEPRECATED* The magic word to utter.", default=u"plugh")

   >>> FallbackDefaultsConfig({u'incantation': u'foo'}).incantation
   u'foo'
   >>> FallbackDefaultsConfig({u'magic_word': u'please'}).incantation
   u'please'
   >>> FallbackDefaultsConfig({}).incantation
   u'xyzzy'


Format string fallback
----------------------

For more complex fallbacks, :class:`FormatStringFieldFallback` can be used.


.. doctest:: fallbacks4

   >>> from confmodel.config import (
   ...     Config, ConfigInt, ConfigText, FormatStringFieldFallback)
   >>> class FormatFallbackConfig(Config):
   ...     """
   ...     This config specification demonstrates format string fallbacks.
   ...     """
   ...     url_base = ConfigText(
   ...         "A host:port pair.", required=True, fallbacks=[
   ...             FormatStringFieldFallback(u"{host}:{port}", ["host", "port"]),
   ...         ])
   ...     host = ConfigText("A hostname.")
   ...     port = ConfigInt("A network port.")

   >>> FormatFallbackConfig({u'url_base': u'example.com:80'}).url_base
   u'example.com:80'
   >>> FormatFallbackConfig({u'host': u'example.org', u'port': 8080}).url_base
   u'example.org:8080'
   >>> FormatFallbackConfig({u'host': u'example.net'}).url_base
   Traceback (most recent call last):
       ...
   ConfigError: Missing required config field 'url_base'


Custom fallbacks
================

If your needs aren't met by the standard fallback classes, you can subclass
:class:`FieldFallback` to implement custom behaviour.

TODO: Write something about custom fallback classes.


.. _static-field-docs:

Static fields
=============

TODO: Write something about static fields.


.. rubric:: Footnotes

.. [#fallback-default]
   Although custom :class:`FieldFallback` subclasses may override this behaviour.
