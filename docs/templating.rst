==============
Templating 101
==============

As Jinja2 is used as the templating engine it is highly recommended to familiarize yourself with Jinja2.

Here are several helpful articles:

* `Jinja2 Background`_

* `About Template Engines`_

.. _`Jinja2 Background`: https://www.fullstackpython.com/jinja2.html

.. _`About Template Engines`: https://www.fullstackpython.com/template-engines.html

And finally the `Jinja2 Template Designer Documentation`_, a must read for Jinja2 template authors.

.. _`Jinja2 Template Designer Documentation`: https://jinja.palletsprojects.com/en/2.10.x/templates


Template Configuration
----------------------

The Template Configuration provides data, influences logic and control structures or points to further resources.

All data of the Template Configuration is available to the Declaration Template as python data structures
and can be accessed through the ``ninja`` namespace.

Template Configuration Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Template Configuration is generated from Template Configuration Files.

Two data formats are supported as Template Configuration Files:

* YAML

* JSON

Combining Multiple Template Configuration Files is supported by AS3 Ninja, we discuss the details later.

.. Note:: There are many Pros and Cons about JSON vs. YAML.
    While it is out of scope to discuss this in detail, YAML is often easier to start with for simple use-cases.
    Two good articles about the challenges YAML and JSON introduce for use as configuration files:

    * `The downsides of JSON for config files`_
    * `YAML: probably not so great after all`_

.. _`The downsides of JSON for config files`: https://www.arp242.net/json-config.html

.. _`YAML: probably not so great after all`: https://www.arp242.net/yaml-config.html

An example:

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 2,4,7-9

    services:
      My Web Service:
        type: http
        address: 198.18.0.1
        irules:
          - ./files/irules/myws_redirects.iRule
        backends:
          - 192.0.2.1
          - 192.0.2.2

The highlighted lines provide data which will be used in the Declaration Template to fill out specific fields,
like the desired name for the service (line 2), its IP address and backend servers.

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 3

    services:
      My Web Service:
        type: http
        address: 198.18.0.1
        irules:
          - ./files/irules/myws_redirects.iRule
        backends:
          - 192.0.2.1
          - 192.0.2.2

On line 3 ``type: http`` is used to indicate the service type.
This information is used in the Declaration Template logic to distinguish between types of services and apply type specific settings.

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 5,6

    services:
      My Web Service:
        type: http
        address: 198.18.0.1
        irules:
          - ./files/irules/myws_redirects.iRule
        backends:
          - 192.0.2.1
          - 192.0.2.2

``irules`` on line 5 references to a list of iRule files.
The logic within the Declaration Template can use this list to load the iRule files dynamically and add them to the service.


as3ninja namespace
^^^^^^^^^^^^^^^^^^

The namespace ``as3ninja`` within the Template Configuration is reserved for AS3 Ninja specific directives and configuration values.

Here is an overview of the current ``as3ninja`` namespace configuration values.

.. code-block:: yaml
    :linenos:

    as3ninja:
      declaration_template: /path/to/declaration_template_file.j2

The ``declaration_template`` points to the Declaration Template File on the filesystem.
It is optional and ignored when a Declaration Template is referenced explicitly, for example through a CLI parameter.

The ``as3ninja`` namespace is accessible under the ``ninja`` namespace, as with any other data from Template Configurations.

.. Caution:: The ``as3ninja`` namespace is reserved and might be used by additional integrations, therefore it should not be used for custom configurations.

Back to our service example:

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 1,2

    as3ninja:
      declaration_template: ./files/templates/main.j2
    services:
      My Web Service:
        type: http
        address: 198.18.0.1
        irules:
          - ./files/irules/myws_redirects.iRule
        backends:
          - 192.0.2.1
          - 192.0.2.2

We extended our Template Configuration with the ``declaration_template`` directive to point to the Declaration Template ``./files/templates/main.j2``.
AS3 Ninja will use this Declaration Template unless instructed otherwise (eg. through a CLI parameter).

Git and the `as3ninja` namespace
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In addition ``as3ninja.git`` is updated during runtime when using AS3 Ninja's `Git` integration.
It holds the below information which can be used in the Declaration Template.

.. code-block:: yaml
    :linenos:

    as3ninja:
      git:
        commit:
          id:       commit id (long)
          id_short: abbreviated commit id
          epoch:    unix epoch of commit
          date:     human readable date of commit
          subject:  subject of commit message
        author:
          name:     author's name of commit message
          email:    author's email
          epoch:    epoch commit was authored
          date:     human readable format of epoch
        branch:     name of the branch

To use the short git commit id within the Declaration Template you would reference it as ``ninja.as3ninja.git.commit.id_short``.


.. Note:: Git Authentication is not explicitly supported by AS3 Ninja.

    However there are several options:

    1. AS3 Ninja invokes the `git` command with privileges of the executing user, hence the same authentication facilities apply.

    2. Implicitly providing credentials through the URL should work: ``https://<username>:<password>@gitsite.domain/repository``

       When using Github: `Personal Access Tokens`_ can be used instead of the user password.

       .. _`Personal Access Tokens`: https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line

    3. `.netrc`_, which can be placed in the docker container at ``/as3ninja/.netrc``, see `confluence.atlassian.com : Using the .netrc file`_ for an example.

    .. _`.netrc`: https://www.gnu.org/software/inetutils/manual/html_node/The-_002enetrc-file.html

    .. _`confluence.atlassian.com : Using the .netrc file`: https://confluence.atlassian.com/bitbucketserver/permanently-authenticating-with-git-repositories-776639846.html#PermanentlyauthenticatingwithGitrepositories-Usingthe.netrcfile


Merging multiple Template Configuration Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

AS3 Ninja supports multiple Template Configuration Files.
This provides great flexibility to override and extend Template Configurations.

Template Configuration Files are loaded, de-serialized and merged in the order specified.
Starting from the first configuration every following configuration is merged into the Template Configuration.
As the de-serialization takes place before merging, JSON and YAML can be combined.


Let's use our previous example, and add two additional Template Configuration Files.
``as3ninja`` is removed for conciseness.


.. code-block:: yaml
    :linenos:
    :emphasize-lines: 5,8-10

    # main.yaml
    services:
      My Web Service:
        type: http
        address: 198.18.0.1
        irules:
          - ./files/irules/myws_redirects.iRule
        backends:
          - 10.0.2.1
          - 10.0.2.2


.. code-block:: yaml
    :linenos:
    :emphasize-lines: 4-7

    # internal_service.yaml
    services:
      My Web Service:
        address: 172.16.0.1
        backends:
          - 172.16.2.1
          - 172.16.2.2


.. code-block:: yaml
    :linenos:
    :emphasize-lines: 4-6

    # backends_dev.yaml
    services:
      My Web Service:
        backends:
          - 192.168.200.1
          - 192.168.200.2


``main.yaml`` is our original example.
``internal_service.yaml`` specifies the same ``My Web Service`` and contains two keys: ``address`` and ``backends``.
``backends_dev.yaml`` again contains our ``My Web Service`` but only lists different ``backends``.

When AS3 Ninja is instructed to use the Template Configurations Files in the order:

  1. ``main.yaml``

  2. ``internal_service.yaml``

AS3 Ninja loads, de-serializes and then merges the configuration. This results in the below python dict.

.. code-block:: python
    :linenos:
    :emphasize-lines: 5,6

    # merged: main.yaml, internal_service.yaml
    {
      'services': {
        'My Web Service': {
          'address': '172.16.0.1',
          'backends': ['172.16.2.1', '172.16.2.2'],
          'irules': ['./files/irules/myws_redirects.iRule'],
          'type': 'http',
        }
      }
    }

``'address'`` and ``'backends'`` was overridden by the data in ``internal_service.yaml``.


When AS3 Ninja is instructed to use all three Template Configurations Files in the order:

    1. ``main.yaml``

    2. ``internal_service.yaml``

    3. ``backends_dev.yaml``

The resulting python dict looks as below.

.. code-block:: python
    :linenos:
    :emphasize-lines: 6

    # merged: main.yaml, internal_service.yaml, backends_dev.yaml
    {
      'services': {
        'My Web Service': {
          'address': '172.16.0.1',
          'backends': ['192.168.200.1', '192.168.200.2'],
          'irules': ['./files/irules/myws_redirects.iRule'],
          'type': 'http',
        }
      }
    }

The ``'address'`` and ``'backends'`` definition was first overridden by the data in ``internal_service.yaml``
and ``'backends'`` was then again overridden by ``backends_dev.yaml``.


.. Important:: Please note that sequences (lists, arrays) are not merged, they are replaced entirely.


Including further Template Configurations using `as3ninja.include` namespace
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Further Template Configuration files can be included using ``include`` within the ``as3ninja`` namespace.

Combined with the ability to merge multiple Template Configuration files, this becomes a powerful feature which can raise complexity. So use with care.


Important rules for using ``as3ninja.include``:

  1. Files included via ``as3ninja.include`` cannot include further Template Configuration files.

  2. All Template Configuration files supplied to `as3ninja` can use ``as3ninja.include``.

  3. Every file included via ``as3ninja.include`` will only be included once, even if multiple configuration files reference this file.

  4. Files will be included in the order specified.

  5. Files are included just after the current configuration file (containing the include statement).

  6. When filename and/or path globbing is used, all matching files will be included alphabetically.

  7. Finally when all includes have been identified ``as3ninja.include`` will be updated with the full list of all includes in the order loaded.


The following example illustrates the behavior.
Suppose we have the below tree structure and three Template Configuration files.

.. code-block:: shell
    :linenos:

    ./configs
    ├── one.yaml
    ├── second
    │   ├── 2a.yaml
    │   ├── 2b.yaml
    │   └── 2c.yaml
    └── third
        ├── 3rd.yaml
        ├── a
        │   ├── 3a.yaml
        │   └── a2
        │       └── 3a2.yaml
        ├── b
        │   ├── 3b1.yaml
        │   └── 3b2.yaml
        └── c
            └── 3c.yaml


.. code-block:: yaml
    :linenos:

    # first.yaml
    as3ninja:
      include: ./configs/one.yaml  # a single file include can use key:value


.. code-block:: yaml
    :linenos:

    # second.yaml
    as3ninja:
      include:  # multiple file includes require a list
        - ./configs/second/2c.yaml  # explicitly include 2c.yaml first
        - ./configs/second/*.yaml  # include all other files
        # The above order ensures that 2c.yaml is merged first and the
        # remaining files are merged afterwards.
        # 2c.yaml will not be imported twice, hence this allows to
        # control merge order with wildcard includes.


.. code-block:: yaml
    :linenos:

    # third.yaml
    as3ninja:
      include:
        - ./configs/third/**/*.yaml  # recursively include all .yaml files
        - ./configs/one.yaml  # try including one.yaml again


This will result in the following list of files, which will be merged to one configuration in the order listed:

.. code-block:: shell
    :linenos:

    first.yaml
    configs/one.yaml
    second.yaml
    configs/second/2c.yaml  # notice 2c.yaml is included first
    configs/second/2a.yaml
    configs/second/2b.yaml
    third.yaml
    configs/third/3rd.yaml
    configs/third/a/3a.yaml
    configs/third/a/a2/3a2.yaml
    configs/third/b/3b1.yaml
    configs/third/b/3b2.yaml
    configs/third/c/3c.yam
    # notice that configs/one.yaml is not included by third.yaml


Assume every YAML file has an ``data: <filename>`` entry and you have a `template.jinja2` with ``{{ ninja | jsonify }}``.

.. code-block:: shell
    :linenos:

    as3ninja transform --no-validate -t template.jinja2 \
      -c first.yaml \
      -c second.yaml \
      -c third.yaml \
      | jq .

would produce:

.. code-block:: json
    :linenos:

    {
      "as3ninja": {
        "include": [
          "configs/one.yaml",
          "configs/second/2c.yaml",
          "configs/second/2a.yaml",
          "configs/second/2b.yaml",
          "configs/third/3rd.yaml",
          "configs/third/a/3a.yaml",
          "configs/third/a/a2/3a2.yaml",
          "configs/third/b/3b1.yaml",
          "configs/third/b/3b2.yaml",
          "configs/third/c/3c.yaml"
        ]
      },
      "data": "configs/third/c/3c.yaml"
    }

.. Note:: The above example is intended to demonstrate the behavior but could be seen as an example for bad practice due to the include complexity.


Including further YAML files using `!include`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

AS3 Ninja uses a custom yaml ``!include`` tag which provides additional functionality to include further YAML files.

``!include`` is followed by a filename (including the path from the current working directory) or a python list of filenames.
The filename(s) can include a globbing pattern following the rules of `python3's pathlib Path.glob`_.

.. _`python3's pathlib Path.glob`: https://docs.python.org/3/library/pathlib.html#pathlib.Path.glob


.. Note:: Nesting ``!include`` is possible, e.g. `a.yaml` includes `b.yaml` which includes `c.yaml` but should be avoided in favor of a cleaner and more understandable design.


Suppose we have the below tree structure:

.. code-block:: shell
    :linenos:

    .
    ├── main.yaml
    └── services
        ├── A
        │   ├── serviceA1.yaml
        │   ├── serviceA2.yaml
        │   └── serviceA3.yaml
        └── B
            ├── serviceB1.yaml
            └── serviceB2.yaml


Each `serviceXY.yaml` file contains definitions for its service, for example:

.. code-block:: yaml
    :linenos:

    ServiceXY:
      address: 198.18.x.y


In `main.yaml` we use ``!include`` to include the `serviceXY.yaml` files as follows:

.. code-block:: yaml
    :linenos:

    # Use globbing to traverse all subdirectories in `./services/`
    # and include all `.yaml` files:
    all_services: !include ./services/**/*.yaml

    # simply include a single yaml file:
    service_a1: !include ./services/A/serviceA1.yaml

    # include a single yaml file but make sure it is included as a list element:
    service_b1_list: !include [./services/B/serviceB1.yaml]

    # include two yaml files explicitly:
    service_a2_b2: !include [./services/A/serviceA2.yaml, ./services/B/serviceB2.yaml]

    # include all files matching serviceB*.yaml in the directory ./services/B/
    services_b: !include ./services/B/serviceB*.yaml


The above yaml describes all syntaxes of ``!include`` and is equivalent to the below yaml.

Please specifically note the behavior for the following examples:

- `all_services` contains a list of all the yaml files the globbing pattern matched.

- `service_a1` only contains the one yaml file, because only one file was specified, it is included as an object not a list.

- `service_a2_b2` contain a list with the entries of serviceA2.yaml and serviceB2.yaml

- `service_b1_list` includes only serviceB1.yaml but as a list entry due to the explicit use of `[]`


.. Note:: Also note that the above paths are relative to the CWD where as3ninja is executed. That means if `ls ./services/A/serviceA2.yaml` is successful running as3ninja from the current directory will work as well.

.. code-block:: yaml
    :linenos:

    all_services:
      - ServiceA2:
          address: 198.18.1.2
      - ServiceA3:
          address: 198.18.1.3
      - ServiceA1:
          address: 198.18.1.1
      - ServiceB2:
          address: 198.18.2.2
      - ServiceB1:
          address: 198.18.2.1

    service_a1:
      ServiceA1:
        address: 198.18.1.1

    service_b1_list:
      - ServiceB1:
          address: 198.18.2.1

    service_a2_b2:
      - ServiceA2:
          address: 198.18.1.2
      - ServiceB2:
          address: 198.18.2.2

    services_b:
      - ServiceB2:
          address: 198.18.2.2
      - ServiceB1:
          address: 198.18.2.1


It is important to note that ``!include`` does not create a "new yaml file" similar to the above example,
instead it de-serializes the `main.yaml` file and treats ``!include`` as an "instruction",
which then de-serializes the files found based on the ``!include`` statement.

So de-serializing the `main.yaml` actually results in the below python data structure (dict):

.. code-block:: python
    :linenos:

    {
      "all_services": [
        { "ServiceA2": { "address": "198.18.1.2" } },
        { "ServiceA3": { "address": "198.18.1.3" } },
        { "ServiceA1": { "address": "198.18.1.1" } },
        { "ServiceB2": { "address": "198.18.2.2" } },
        { "ServiceB1": { "address": "198.18.2.1" } }
      ],
      "service_a1": { "ServiceA1": { "address": "198.18.1.1" } },
      "service_b1_list": [
        { "ServiceB1": { "address": "198.18.2.1" } }
      ],
      "service_a2_b2": [
        { "ServiceA2": { "address": "198.18.1.2" } },
        { "ServiceB2": { "address": "198.18.2.2" } }
      ],
      "services_b": [
        { "ServiceB2": { "address": "198.18.2.2" } },
        { "ServiceB1": { "address": "198.18.2.1" } }
      ]
    }





.. Caution:: ``!include`` does not prevent against circular inclusion loops, which would end in a RecursionError exception.


Default Template Configuration File
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If no Template Configuration File is specified, AS3 Ninja will try to use the first of the following files.

    1. ``./ninja.json``

    2. ``./ninja.yaml``

    3. ``./ninja.yml``

This is useful if you do not need multiple Template Configuration Files or only occasionally need them.


Declaration Template
--------------------

The Declaration Template defines how the configuration is used to render an AS3 Declaration.

Declaration Templates use the Template Configuration, which is available in the Jinja2 Context.


A question of paradigms: Declarative or Imperative
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you thought you already choose the declarative paradigm with AS3 you are mostly correct.
The AS3 Declaration is declarative.

But how do you produce the AS3 Declaration?

This is where AS3 Ninja and specifically Jinja2 comes into play.
Jinja2 provides a wide spectrum between declarative and imperative to fit your specific needs.


A quick overview of Imperative vs. Declarative Programming, which can help understand the topic better: `Imperative vs Declarative Programming`_

.. _`Imperative vs Declarative Programming`: https://tylermcginnis.com/imperative-vs-declarative-programming/


AS3 Ninja the declarative way
*****************************

Let's look at a declarative way to render an AS3 Declaration.

.. code-block:: jinja
    :linenos:
    :emphasize-lines: 7,8,10,19,25

    {# Declaration Template #}
    {
      "class": "AS3",
      "declaration": {
        "class": "ADC",
        "schemaVersion": "3.11.0",
        "id": "urn:uuid:{{ ninja.uuid }}",
        "{{ ninja.tenant }}": {
          "class": "Tenant",
          "{{ ninja.app.name }}": {
            "class": "Application",
            "template": "http",
            "backends": {
              "class": "Pool",
              "monitors": ["http"],
              "members": [
                {
                  "servicePort": 80,
                  "serverAddresses": [ {{ ninja.app.backends }} ]
                }
              ]
            },
            "serviceMain": {
              "class": "Service_HTTP",
              "virtualAddresses": ["{{ ninja.app.address }}"],
              "pool": "backends"
            }
          }
        }
      }
    }

The above Declaration Template uses Jinja2 to fill specific values using variables.
No logic, no control structures nor commands are used.

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 7

    # Template Configuration
    tenant: MyTenant
    uuid: 2819307c-d8c3-4d1e-911e-40889e1df6c7
    app:
      name: MyApp
      address: 198.18.0.1
      backends: "\"192.168.0.1\", \"192.168.0.2\""

Above is an example Template Configuration for our Declaration Template.
As our backends are expected to be a JSON array, the value of ``backends`` isn't very pretty.


Adding additional services, tenants or service specific configurations will require changes
in the Template Configuration as well as the Declaration Template.

AS3 Ninja the imperative way
****************************

Now let's find an imperative way to render a similar AS3 Declaration.

.. code-block:: jinja
    :linenos:
    :emphasize-lines: 8,11,18,20,22,31,32,34,35

    {# Declaration Template #}
    {
      "class": "AS3",
      "declaration": {
        "class": "ADC",
        "schemaVersion": "3.11.0",
        "id": "urn:uuid:{{ uuid() }}",
        {% for tenant in ninja.tenants %}
        "{{ tenant.name }}": {
          "class": "Tenant",
          {% for app in tenant.apps %}
          "{{ app.name }}": {
            "class": "Application",
            "template": "{{ app.type }}",
            "backends": {
              "class": "Pool",
                "monitors":
                {% if app.monitors is defined %}
                    {{ app.monitors | jsonify }},
                {% else %}
                    {{ ninja.mappings.monitor[app.type] | jsonify }},
                {% endif %}
                "members": {{ app.backends | jsonify }}
            },
            "serviceMain": {
              "class": "{{ ninja.mappings.service[app.type] }}",
              "virtualAddresses": {{ app.address | jsonify }},
              "pool": "backends"
            }
          }
        {% if not loop.last %},{% endif %}
        {% endfor %}
        }
      {% if not loop.last %},{% endif %}
      {% endfor %}
      }
    }

This Declaration Template not only uses Jinja2 to fill specific values using variables but also
uses control structures, mainly loops and conditions (highlighted), to render the AS3 Declaration.

You can already see that this Declaration Template iterates over a list of tenants and a list of apps for each tenant.
This clearly shows this example is probably easy to extend with additional tenants and apps.

As this Declaration Template contains a lot more details we will take a closer look at each step,
but first let's have a look at the Template Configuration:

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 9-13

    # Template Configuration
    tenants:
    - name: MyTenant
      apps:
      - name: MyApp
        type: http
        address:
        - 198.18.0.1
        backends:
        - servicePort: 80
          serverAddresses:
          - 192.168.0.1
          - 192.168.0.2
    mappings:
      service:
        http: Service_HTTP
      monitor:
        http:
        - http

The Template Configuration is longer than the previous *declarative* example, but it is also more flexible.
The non-pretty representation of the backends has been replaced with a more flexible ``backends`` definition (highlighted).

As this Configuration Template works hand in hand with the Declaration Template we will take a closer look at both in the next section.

Building a Declaration Template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A *declarative* Declaration Template and the corresponding Template Configuration is pretty straightforward as you saw earlier.

So instead we will look at the *imperative* example above and walk through each step.
For conciseness we will remove parts from the Declaration Template and Template Configuration and focus on the subject.

Looping Tenants and their Apps
******************************

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 2-3,5-6

    # Template Configuration
    tenants:
    - name: MyTenant
      # ... tenant specific configuration
      apps:
      - name: MyApp
        type: http
        # ... app specific configuration

The above Template Configuration excerpt contains a list of Tenants (line 2) with the first list entry having ``name`` key with value ``MyTenant`` (line 3).
Within this Tenant a list of Applications (Apps) is defined (line 5), with the first list entry having a ``name`` key with value ``MyApp`` (line 6).

.. code-block:: jinja
    :linenos:
    :emphasize-lines: 5,6,8,9,12,13,15,16

    {# Declaration Template #}
    {
      "class": "AS3",
      {# ... more code ... #}
        {% for tenant in ninja.tenants %}
        "{{ tenant.name }}": {
          "class": "Tenant",
          {% for app in tenant.apps %}
          "{{ app.name }}": {
          {# ... app specific code ... #}
          }
        {% if not loop.last %},{% endif %}
        {% endfor %}
        }
      {% if not loop.last %},{% endif %}
      {% endfor %}
      }
    }

The Declaration Template is built to iterate over a list of Tenants (line 5).
The Template Configuration list of Tenants is accessible via ``ninja.tenants`` and each Tenant is assigned to ``tenant``, which is now available within the for loop.
On line 6 the Tenant name is read from ``tenant.name``.

Furthermore on line 8 the Declaration Template will iterate the list of Applications defined for this Tenant.
The list of Applications for this particular Tenant is available via ``tenant.apps``. ``apps`` refers to the definition in the Template Configuration (on line 5).
The Application specific configuration starts on line 9, where ``app.name`` is used to declarative the Application class of the AS3 Declaration.

Line 12 is checking for the last iteration of the inner "Application loop" and makes sure the comma (``,``) is included when there are further elements in the Application list.
This is important as `JSON does not tolerate a trailing comma <https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Trailing_commas#Trailing_commas_in_JSON>`_.
Line 13 defines the end of the loop.

The same is done on line 15 and 16 for the outer "Tenants loop".

.. Note:: More details on control structures in Jinja2 can be found at `List of Control Structures <https://jinja.palletsprojects.com/en/2.10.x/templates/#list-of-control-structures>`_ in the Jinja2 Template Designer Documentation.


Application specific settings
*****************************

Now let's look at the Application specific settings.

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 5-19

    # Template Configuration
    tenants:
    - name: Tenant1
      apps:
      - name: MyApp
        type: http
        address:
        - 198.18.0.1
        backends:
        - servicePort: 80
          serverAddresses:
          - 192.168.0.1
          - 192.168.0.2
    mappings:
      service:
        http: Service_HTTP
      monitor:
        http:
        - http

The YAML is more structured to not only fit the Declaration Template but also the AS3 data structures.
A ``mappings`` data structure was added to assist with default values / mappings to Application types.

.. code-block:: jinja
    :linenos:
    :emphasize-lines: 5,9-14,17,18

    {# Declaration Template #}
      {# ... more code ... #}
      "{{ app.name }}": {
        "class": "Application",
        "template": "{{ app.type }}",
        "backends": {
          "class": "Pool",
            "monitors":
            {% if app.monitors is defined %}
                {{ app.monitors | jsonify }},
            {% else %}
                {{ ninja.mappings.monitor[app.type] | jsonify }},
            {% endif %}
            "members": {{ app.backends | jsonify }}
        },
        "serviceMain": {
          "class": "{{ ninja.mappings.service[app.type] }}",
          "virtualAddresses": {{ app.address | jsonify }},
          "pool": "backends"
        {# ... more code ... #}

The ``app.type`` is used on line 5 to map to the ``http`` AS3 template,
on line 12 ``app.type`` is used again as a key for ``mappings.service``.
This allows us to create multiple `App type` to `Service_<type>` mappings.
In this case ``http`` maps to the AS3 service class ``Service_HTTP``.

Line 9-13 deals with monitors, if ``app.monitors`` is defined it is used,
otherwise ``app.type`` is used again to lookup the default monitor to use, based on the Template Configuration (line 17-19).
Note that ``"monitors"`` is expected to be a JSON array of monitors, this is why the Template Configuration YAML uses a list for ``monitor.http``.
``jsonify`` is an AS3 Ninja Filter (see :py:func:`as3ninja.jinja2.filterfunctions.jsonify`) which will convert any "piped" data to a valid JSON format.
A python list (which the YAML de-serializes to) is converted to a JSON array.

The ``"members"`` key for a `AS3 Pool class` is expected to be a list, each list entry is an object with several key:value pairs.
``serverAddresses`` are again expected to be a list of IP addresses.

Looking at the ``backends`` part of the Template Configuration again:

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 2,4,5

        backends:
        - servicePort: 80
          serverAddresses:
          - 192.168.0.1
          - 192.168.0.2

``app.backends`` and it's YAML exactly represents this structure, making it easy for the Declaration Template to just convert it to JSON (using the ``jsonify`` filter).
Sometimes it is easier to look at the resulting JSON, as it is used by AS3 as well.
Here is how the above YAML for ``backends`` looks like:

.. code-block:: json
    :linenos:
    :emphasize-lines: 2,5,7

    {
      "backends": [
        {
          "servicePort": 80,
          "serverAddresses": ["192.168.0.1", "192.168.0.2"]
        }
      ]
    }


``"virtualAddresses"``, on line 18 Declaration Template, is also expected to be a JSON array, which is what the Template Configuration perfectly represents and ``jsonify`` converts to.


Adding more Tenants
*******************

Based on the above *imperative* example, it is easy to add further Tenants.

Here is an example adding one more Tenant:

.. code-block:: yaml
    :linenos:

    # Template Configuration
    tenants:
    - name: Tenant1
      apps:
      - name: MyApp
        type: http
        address:
        - 198.18.0.1
        backends:
        - servicePort: 80
          serverAddresses:
          - 192.168.0.1
          - 192.168.0.2
    - name: Tenant2
      apps:
      - name: TheirApp
        type: http
        address:
        - 198.18.100.1
        monitors:
        - http
        - icmp
        backends:
        - servicePort: 80
          serverAddresses:
          - 192.168.100.1
    mappings:
      service:
        http: Service_HTTP
      monitor:
        http:
        - http

Adding an additional App type
*****************************

What if we want to add an additional type of Application?
Let's assume we want to add a SSH server, using AS3's `Service_TCP`.

As this service class doesn't come with a default value for
``virtualPort`` we will need to modify our Declaration Template.

.. code-block:: jinja
    :linenos:
    :emphasize-lines: 26-28

    {# Declaration Template #}
    {
      "class": "AS3",
      "declaration": {
        "class": "ADC",
        "schemaVersion": "3.11.0",
        "id": "urn:uuid:{{ uuid() }}",
        {% for tenant in ninja.tenants %}
        "{{ tenant.name }}": {
          "class": "Tenant",
          {% for app in tenant.apps %}
          "{{ app.name }}": {
            "class": "Application",
            "template": "{{ app.type }}",
            "backends": {
              "class": "Pool",
                "monitors":
                {% if app.monitors is defined %}
                    {{ app.monitors | jsonify }},
                {% else %}
                    {{ ninja.mappings.monitor[app.type] | jsonify }},
                {% endif %}
                "members": {{ app.backends | jsonify }}
            },
            "serviceMain": {
              {% if app.port is defined %}
              "virtualPort": {{ app.port }},
              {% endif %}
              "class": "{{ ninja.mappings.service[app.type] }}",
              "virtualAddresses": {{ app.address | jsonify }},
              "pool": "backends"
            }
          }
        {% if not loop.last %},{% endif %}
        {% endfor %}
        }
      {% if not loop.last %},{% endif %}
      {% endfor %}
      }
    }

We added a conditional check for ``app.port`` (line 26-28).
If it is set, ``"virtualPort"`` will be added to the AS3 Declaration with the value of ``app.port``.
Of course this ``app.port`` can be used by other service types as well.

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 27-35,39,43,44

    # Template Configuration
    tenants:
    - name: Tenant1
      apps:
      - name: MyApp
        type: http
        address:
        - 198.18.0.1
        backends:
        - servicePort: 80
          serverAddresses:
          - 192.168.0.1
          - 192.168.0.2
    - name: Tenant2
      apps:
      - name: TheirApp
        type: http
        address:
        - 198.18.100.1
        monitors:
        - http
        - icmp
        backends:
        - servicePort: 80
          serverAddresses:
          - 192.168.100.1
      - name: TcpApp
        type: tcp
        port: 22
        address:
        - 198.18.100.1
        backends:
        - servicePort: 22
          serverAddresses:
          - 192.168.100.1
    mappings:
      service:
        http: Service_HTTP
        tcp: Service_TCP
      monitor:
        http:
        - http
        tcp:
        - tcp

Line 29 has the new ``port`` key, which is used in the Declaration Template.
Along with the TCP based service we also updated the mappings.


.. Hint:: If you use Visual Studio Code, the `jinja-json-syntax`_ Syntax Highlighter is very helpful.

.. _`jinja-json-syntax`: https://marketplace.visualstudio.com/items?itemName=ryanrhee.jinja-json-syntax
