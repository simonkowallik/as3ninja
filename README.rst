=========
AS3 Ninja
=========

.. .. image:: https://img.shields.io/pypi/v/as3ninja.svg
        :target: https://pypi.python.org/pypi/as3ninja

.. image:: https://img.shields.io/travis/simonkowallik/as3ninja.svg
        :target: https://travis-ci.com/simonkowallik/as3ninja

.. image:: https://readthedocs.org/projects/as3ninja/badge/?version=latest
        :target: https://as3ninja.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


* Free software: ISC license
* Documentation: https://as3ninja.readthedocs.io.
* Works with Python 3.7 and up


.. Note:: Please note that AS3 Ninja is in an early stage. Many things might change in a short time.

What's AS3 Ninja?
-----------------

AS3 Ninja is a templating engine as well as a validator for `AS3`_ declarations. It provides a CLI for local usage, as well as a OpenAPI/Swagger based REST API.

.. _AS3: https://github.com/F5Networks/f5-appsvcs-extension/


In short, you want it in your deck!


.. code-block:: text

                +---------------+
                |  _            |
                |  \\    ,      |
                |   \\ (**)~    |
                |    \\ AS3 ,%  |
                |      Ninja    |
                |      /   \    |
                +---------------+
                |  API  |  CLI  |
                +---------------+


Features
--------

* Validate your AS3 Declarations against the AS3 Schema (via API, eg. for CI/CD)
* Create AS3 Declarations from templates using the full power of Jinja2 (CLI and API)

   * reads your JSON or YAML configurations to generate AS3 Declarations
   * carefully crafted Jinja2 :py:mod:`as3ninja.filters` and :py:mod:`as3ninja.functions` further enhance the templating capabilities

* Git(hub) is supported to pull configurations and declaration templates for transformation
* Vault by Hashicorp is (going to be) supported to retrieve secrets
* AS3 Ninja provides a simple CLI...
* and a REST API including a Swagger/OpenAPI interface at ``/api/docs`` and ``/api/redoc``


AS3 Ninja Interface
-------------------

Impressions from the AS3 Ninja interfaces:

the Command Line
^^^^^^^^^^^^^^^^
as3ninja cli:

.. image:: _static/_cli.svg

the API UI
^^^^^^^^^^
ReDoc and Swagger UI:

.. image:: _static/_api.gif

Swagger UI demo:

.. image:: _static/_api_demo.gif


Where to start?
---------------

* :doc:`usage`
* :doc:`templating`
* :doc:`examples`


Security Notes
--------------

AS3 Ninja's focus is flexibilty in templating and features,
it is not harded to run in untrusted environments.

* It comes with a large set of dependencies, all of them might introduce security issues
* Jinja2 is not using a Sandboxed Environment (yet) and the `readfile` filter allows arbitary file includes.
* The API is unauthenticated (for now)


.. DANGER:: Only use AS3 Ninja in a trusted environment with restricted access and trusted input.


.. This package was created with Cookiecutter_ and the `elgertam/cookiecutter-pipenv`_ project template, based on `audreyr/cookiecutter-pypackage`_.

.. .. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. .. _`elgertam/cookiecutter-pipenv`: https://github.com/elgertam/cookiecutter-pipenv
.. .. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
