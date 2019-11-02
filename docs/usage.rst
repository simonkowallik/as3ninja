.. highlight:: shell

===============
Using AS3 Ninja
===============


Using with Docker
-----------------

Starting an ephemeral container for use of the API:

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

Docker :: Command Line Usage
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using docker to run the command line, mapping the ``./examples`` folder to the container.
The ``as3ninja`` cli app has therefore access to the examples and can transform the Declaration Template unsing the Template Configuration.

.. code-block:: shell

    docker run -v $(pwd)/examples:/examples -ti as3ninja \
      as3ninja transform -c examples/simple/ninja.yaml --pretty | less

The second line is the actual as3ninja command which is executed inside the container (which has the same name).


If you wonder why no Declaration Template is specified on the command line, the reason is that the template is referenced within the Template Configuration.

The following statement within the ``ninja.yaml`` provides the template location to as3ninja:

.. code-block:: yaml

    as3ninja:
      declaration_template: "examples/simple/template.j2"

.. image:: _static/_docker_cli.svg

.. todo:: more cli examples


Command Line Usage
------------------

.. todo:: direct command line usage after installation with pip


API Usage
---------

Use ``curl`` or ``httpie`` to query all available AS3 Schema versions:

.. code-block:: shell

    http localhost:8000/api/schema/versions


.. image:: _static/_curl_api.svg

Navigate to `http://localhost:8000/api/docs`_ and `http://localhost:8000/api/redoc`_

.. _`http://localhost:8000/api/docs`: http://localhost:8000/api/docs

.. _`http://localhost:8000/api/redoc`: http://localhost:8000/api/redoc


.. todo:: postman examples for api usage



Python Package
--------------

To use AS3 Ninja in a project::

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


.. todo:: Enhance Python Package description
