========
Concepts
========

To get started with AS3 Ninja first let's look at the concept.


The objective is to generate `AS3 Declarations` from templates where the parameterization of the template is done using a configuration.


AS3 Ninja uses the following main components to achieve this:

* Templates (Jinja2)
* Configurations (YAML and/or JSON)

The templates are also referred to as `Declaration Templates`, the configuration is referred to as `Template Configuration`.


AS3 Ninja doesn't force you into a declarative or imperative paradigm.
You can just "fill the blanks" (declarative) or implement excessive logic within the `Declaration Templates` (imperative).


Workflow
--------

The workflow to generate a deployable `AS3 Declaration` is a follows:

1. Get the `Declaration Template` and `Template Configuration` from the local filesystem or `Git`
2. Load, de-serialize and merge all `Template Configurations`
3. Feed the `Declaration Template` and `Template Configuration` to Jinja2
4. Render the `AS3 Declaration` using jinja2 ("transform the `Declaration Template` using the `Template Configuration`")
5. Validate the `AS3 Declaration` against the `AS3 Schema` (optional)

This workflow is also referred to as `transformation`.

Components
----------
Let's look at the components at play.

Here is a diagram.


The AS3 Ninja ecosystem
^^^^^^^^^^^^^^^^^^^^^^^


.. code-block:: text

    +-----------------+               +----------------+
    |                 |               |                |
    | HashiCorp Vault +--------+      |   AS3 Schema   |
    |                 |        |      |                |
    +-----------------+        |      +-------+--------+
                               |              ^
                               |              |
                               |              |
                               |        +-----+------+
                               +------->+_           |
    +------------------+                |\\    ,     |              +---------------------+
    |                  |                | \\ (**)~   |              |                     |
    | Git(Hub/Lab/Tea) +--------------->+  \\ AS3 ,% +------------->+   AS3 Declaration   |
    |  or filesystem   |                |    Ninja   |              |                     |
    |                  |                |    /   \   |              +---------------------+
    +-+----------------+                +------------+
      |                                 | API || CLI |
      |                                 +--+------+--+
      |                                    ^      ^
      +--[Declaration Template(s)]----+    |      |
      |                               +----+------+
      +--[Template Configuration(s)]--+



AS3 Declaration
^^^^^^^^^^^^^^^
The `AS3 Declaration` is the JSON file ready to be pushed to the AS3 API. In DevOps terms it is an `artifact`_ (see also `here`_).
It contains all configuration elements needed for AS3 to create the configuration.

.. _`artifact`: https://en.wikipedia.org/wiki/Artifact_(software_development)
.. _`here`: https://devops.stackexchange.com/questions/466/what-is-an-artifact-or-artefact

.. Note:: `AS3 Declarations` often contain very sensitive data, like cryptographic keys or passwords.


Declaration Templates
^^^^^^^^^^^^^^^^^^^^^
Declaration Templates are Jinja2 templates, which can include further templates for specific `AS3 Declaration` components, e.g. for pools or profiles.
Jinja2 offers a variety of imperative programming techniques like control structures.

The `Jinja2 Template Designer Documentation`_ is a highly recommended read.

.. _`Jinja2 Template Designer Documentation`: https://jinja.palletsprojects.com/en/2.10.x/templates

Filters and Functions
"""""""""""""""""""""
Jinja2 offers filters and functions which can be used in templates.

AS3 Ninja comes with additional filters and functions which are specifically aimed at AS3.

See also:

* :py:mod:`as3ninja.jinja2.filterfunctions`
* :py:mod:`as3ninja.jinja2.filters`
* :py:mod:`as3ninja.jinja2.functions`
* :py:mod:`as3ninja.jinja2.tests`


Template Configuration
^^^^^^^^^^^^^^^^^^^^^^
The `Template Configuration` are one or more YAML or JSON files. These define various variables, lists and in general contain data to be used in the `Declaration Template(s)`.

Multiple configuration files can be combined, where settings within the previous file are updated by all following files.
This is quite powerful, as it allows to overwrite ("overlay") specific configuration parameters, for example for different environments (DEV/QA/PROD).

.. Note:: It is recommended to avoid storing secrets within the Template Configuration.

AS3 Schema
^^^^^^^^^^
Once the `AS3 Declaration` is generated from the `Declaration Template` using the `Template Configuration`, the resulting `artifact` can be validated against the `AS3 Schema`, which is available on the `GitHub AS3 Repository`_.

.. _`GitHub AS3 Repository`: https://github.com/F5Networks/f5-appsvcs-extension/tree/master/schema

.. Note:: AS3 Ninja doesn't need to generate the `AS3 Declaration` to validate it. Any other declaration can be validated against the `AS3 Schema` using the API.


Git
^^^
`Git` has not only conquered the world of version control systems but is also very handy when you need to save, version, track and rollback any kind of configuration files. Therefore `Git` is a perfect place to store `Declaration Template(s)` as well as `Template Configuration(s)`.

AS3 Ninja can fetch from `Git` and automatically generate an `AS3 Declaration` for you.


Vault
^^^^^
`AS3 Declarations` often contain very sensitive data, these are commonly called `secrets` in the DevOps context.
Hashicorp's Vault is a well established platform to manage any kind of secret and AS3 Ninja uses `hvac`_ to interface with vault.

AS3 Ninja retrieves relevant secrets during the transformation of the `AS3 Declaration`.
The `Declaration Template` contains functions / filters which communicate to vault based on the settings within the template as well as the `Template Configuration`.

.. _`hvac`: https://github.com/hvac/hvac

See :doc:`Vault Integration <vault>` for further details.
