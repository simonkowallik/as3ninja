========
Concepts
========

To get started with AS3 Ninja first let's look at the concept.


The objective is to generate `AS3 Declarations` from templates where the  parameterization of the template is done using a configuration.


AS3 Ninja uses the following main components to achive this:

* Templates (Jinja2)
* Configurations (YAML and/or JSON)

The templates are also refered to as `Declaration Templates`, the configuration is often refered to as `Template Configuration`.


Workflow
--------

The workflow to generate a deployable `AS3 Declaration` is a follows:

1. Get the `Declaration Template`s and `Template Configuration` from the local filesystem or `Git`
2. Load the `Template Configuration` and optionally enrich it with more data
3. Feed the `Declaration Template` and `Template Configuration` to Jinja2
4. Render the `AS3 Declaration`
5. Validate the `AS3 Declaration` against the `AS3 Schema` (optional)



Components
----------
Let's look at the components at play.

Here is a diagramm.


The AS3 Ninja
^^^^^^^^^^^^^


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
    |                  |                |    Ninja   |              |                     |
    +-+----------------+                |    /   \   |              +---------------------+
      |                                 +------------+
      |                                 | API || CLI |
      |                                 +--+------+--+
      |                                    ^      ^
      +--[Declaration Template]----+       |      |
      |                            +-------+------+
      +--[Template Configuration]--+



AS3 Declaration
^^^^^^^^^^^^^^^
The `AS3 Declaration` is the JSON file ready to be pushed to the AS3 API. In DevOps terms it is an `artifact`_ (see also `here`_).
It contains all configuration elements needed for AS3 to create the configuration. `AS3 Declarations` often contain very sensitive data, like cryptographic keys or passwords as well.

.. _`artifact`: https://en.wikipedia.org/wiki/Artifact_(software_development)
.. _`here`: https://devops.stackexchange.com/questions/466/what-is-an-artifact-or-artefact

Declaration Templates
^^^^^^^^^^^^^^^^^^^^^
Declaration Templates are Jinja2 templates, which can include further templates for specific `AS3 Declaration` components, like pools or profiles.

Filters and Functions
"""""""""""""""""""""
Jinja2 offers filters and functions which can be used in templates.

AS3 Ninja comes with additional filters and functions which are specifically aimed at AS3.

See also:

* :py:mod:`as3ninja.filters`
* :py:mod:`as3ninja.functions`


Template Configuration
^^^^^^^^^^^^^^^^^^^^^^
The `Template Configuration` are one or more YAML or JSON files. These define various variables, lists and in general contain data to be used in the `Declaration Template(s)`.

Multiple configration files can be combined, where settings within the previous file are updated by all following files.
This is quite powerfull, as it allows to overwrite ("overlay") specific configuration parameters, for example for different environments (DEV/QA/PROD).

AS3 Schema
^^^^^^^^^^
Once the `AS3 Declaration` is generated from the `Declaration Template` using the `Template Configuration`, the resulting `artifact` can be validated against the `AS3 Schema`, which is available on the `GitHub AS3 Repository`_.

AS3 Ninja doesn't need to generate the `AS3 Declaration`, any other declaration can be validated against the `AS3 Schema` using the API.

.. _`GitHub AS3 Repository`: https://github.com/F5Networks/f5-appsvcs-extension/tree/master/schema

Git
^^^
`Git` has not only conquered the world of source version control but is also very handy when you need to save, version, track and rollback any kind of configuration files. Therefore `Git` is a perfect place to store `Declaration Template(s)` as well as `Template Configuration(s)`.

AS3 Ninja can fetch from `Git` and automatically generate an `AS3 Declaration` for you.


Vault
^^^^^
`AS3 Declarations` often contain very sensitive data, these are commonly called `secrets` in the DevOps context.
Hashicorp's Vault is a well established platform to manage any kind of secret and AS3 Ninja uses `hvac`_ to interface with vault.
The idea is to fetch relevant secrets during generation of the `AS3 Declaration`. The `Declaration Template` talks to vault based on the settings within the template as well as the `Template Configuration`.

.. _`hvac`: https://github.com/hvac/hvac


.. todo:: add link to vault filter/function
