
===============
Using AS3 Ninja
===============


Run AS3 Ninja with Docker
-------------------------

Starting an ephemeral/temporary container for use of the API:

.. code-block:: shell

   docker run -it --rm -p 8000:8000 simonkowallik/as3ninja


.. image:: _static/_docker_ephemeral.svg

Creating a persistent container for CLI and API usage:

.. code-block:: shell

   docker container create --name as3ninja -p 8000:8000 simonkowallik/as3ninja

   # start the as3ninja container in background
   docker start -a as3ninja


.. image:: _static/_docker_persistent.svg


.. Important::
   The AS3 Schema files need to be downloaded from github.com to validate AS3 Declarations.
   AS3 Ninja :py:meth:`as3ninja.AS3Schema.updateschemas` is doing that for you automatically,
   but the Docker Container will need access to https://github.com.

Using the CLI with Docker
^^^^^^^^^^^^^^^^^^^^^^^^^

Docker can be used to run the command line.

.. code-block:: shell

   $ tree ./examples/simple/
   ./examples/simple/
   ├── http_path_header.iRule
   ├── ninja.yaml
   ├── sorry_page.iRule
   └── template.j2

This example assumes the relevant Template Configurations and Declaration Templates are stored in ``./examples/simple``.

.. code-block:: yaml
   :linenos:
   :emphasize-lines: 2

   as3ninja:
     declaration_template: "examples/simple/template.j2"

The ``declaration_template`` statement within the ``ninja.yaml`` provides the template location as ``examples/simple/template.j2``.
as3ninja expects to find the template at this location.

.. code-block:: shell
   :linenos:
   :emphasize-lines: 2,3,4

   $ docker run --rm --tty --interactive \
       --volume \$(pwd)/examples:/examples \
       simonkowallik/as3ninja:latest \
       as3ninja transform -c /examples/simple/ninja.yaml \
       | jq ."

Instructs docker to bind mount the ``$(pwd)/examples`` folder to ``/examples`` (line 2) for the container image ``simonkowallik/as3ninja:latest`` (line 3).

Docker then executes ``as3ninja transform -c /examples/simple/ninja.yaml`` (line 4) within the container and pipes the result to ``jq .``.

.. image:: _static/_docker_cli.svg

.. todo:: more cli examples


Command Line Usage
------------------

.. code-block:: shell

    # for system wide installation (not recommended)
    git clone https://github.com/simonkowallik/as3ninja
    cd as3ninja
    python3 setup.py install

.. code-block:: shell

    git clone https://github.com/simonkowallik/as3ninja
    cd as3ninja
    pipenv install
    pipenv shell

.. Note:: For now AS3 Ninja is not available on PyPI and system wide installation is not recommended. Using docker or a virtualenv/pipenv is recommended.

API Usage
---------

Use ``curl`` or ``httpie`` to query all available AS3 Schema versions:

.. code-block:: shell

   $ http localhost:8000/api/schema/versions

   $ curl -s localhost:8000/api/schema/versions | jq .

.. image:: _static/_httpie_api.svg

Navigate to `http://localhost:8000/docs`_ and `http://localhost:8000/redoc`_ to explore the API.

.. _`http://localhost:8000/docs`: http://localhost:8000/docs

.. _`http://localhost:8000/redoc`: http://localhost:8000/redoc


.. todo:: Postman collection for API calls


Python Package
--------------

To use AS3 Ninja in your project:

.. code-block:: python
   :linenos:

   from as3ninja import schema, declaration

   # Declaration Template (str)
   declaration_template = """
   {
       "class": "AS3",
       "declaration": {
           "class": "ADC",
           "schemaVersion": "3.11.0",
           "id": "urn:uuid:{{ uuid() }}",
           "{{ ninja.Tenantname }}": {
               "class": "Tenant"
           }
       }
   }
   """

   # Template Configuration (dict)
   template_configuration = {
       "Tenantname": "MyTenant"
   }

   # generate the AS3 Declaration
   as3declaration = declaration.AS3Declaration(
       template_configuration=template_configuration,
       declaration_template=declaration_template
       )

   from pprint import pprint
   pprint(as3declaration.declaration)
   {'class': 'AS3',
    'declaration': {'MyTenant': {'class': 'Tenant'},
                    'class': 'ADC',
                    'id': 'urn:uuid:f3850951-4a63-43ec-b2a3-28ab2c315479',
                    'schemaVersion': '3.11.0'}}

   # a AS3 schema instance
   as3schema = schema.AS3Schema()

   # Validate the AS3 Declaration against the AS3 Schema (latest version)
   try:
       as3schema.validate(declaration=as3declaration.declaration)
   except schema.AS3ValidationError:
       raise


.. todo:: Improve documentation for usage as python package
