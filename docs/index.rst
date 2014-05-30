.. confmodel documentation master file, created by
   sphinx-quickstart on Thu May 29 15:06:07 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

====================================================================
confmodel: A declarative configuration access and validation system.
====================================================================

confmodel is a tool for accessing, validating, and documenting configuration
parameters. Config specifications are written as Python classes with
specialised field attributes (similar to Django forms) and then instantiated
with configuration data. The configuration is validated and fields are
available as parameters on the config object (similar to Django models,
although read-only).


Installation
============

.. code-block:: bash

   $ pip install confmodel


Documentation
=============

.. toctree::
   :maxdepth: 2

   overview
   api

