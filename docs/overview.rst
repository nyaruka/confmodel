
========
Overview
========


A config specification is a subclass of :class:`~confmodel.config.Config` with some field attributes.


.. testcode:: example1

   from confmodel.config import Config, ConfigInt, ConfigText

   class MyConfig(Config):
       """
       This is a demo config specification.

       It's important to write a docstring for the class and to put helpful
       information into the mandatory ``doc`` parameter in each field.
       """

       incantation = ConfigText("The incantation to recite.", required=True)
       magic_number = ConfigInt("A magic number.", default=42)

Once the specification has been defined, it can be used to access configuration data acquired from some arbitrary source.

.. doctest:: example1

   >>> config = MyConfig({'incantation': 'Open sesame!'})
   >>> config.incantation
   'Open sesame!'
   >>> config.magic_number
   42

The data is validated when the config object is instantiated, so you'll know immediately if something is wrong.

.. doctest:: example1

   >>> config = MyConfig({})  # No configuration data.
   Traceback (most recent call last):
       ...
   ConfigError: Missing required config field 'incantation'

This is useful, but we need a way to tell people what configuration is required. Fortunately, confmodel generates ReST docstrings for your config classes, suitable for inclusion in Sphinx documentation.

.. doctest:: example1

   >>> print MyConfig.__doc__
   This is a demo config specification.
   <BLANKLINE>
   It's important to write a docstring for the class and to put helpful
   information into the mandatory ``doc`` parameter in each field.
   <BLANKLINE>
   Configuration options:
   <BLANKLINE>
   :param str incantation:
   <BLANKLINE>
       The incantation to recite.
   <BLANKLINE>
   :param int magic_number:
   <BLANKLINE>
       A magic number.

.. admonition:: Rendered documentation for ``MyConfig``:

   .. class:: MyConfig

      This is a demo config specification.

      It's important to write a docstring for the class and to put helpful
      information into the mandatory ``doc`` parameter in each field.

      Configuration options:

      :param str incantation:

          The incantation to recite.

      :param int magic_number:

          A magic number.
