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

Let's look at a declarative way to specify an AS3 Declaration.

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

.. code-block:: jinja
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
Adding additional services, tenants or service specific configurations will require changes in the Template Configuration as well as the Declaration Template.

AS3 Ninja the imperative way
****************************

.. todo:: imperative example


Building a Declaration Template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. todo:: outline a Declaration Template for the previous Template Configuration example


.. Hint:: If you use Visual Studio Code, the `jinja-json-syntax`_ Syntax Highlighter is very helpful.

.. _`jinja-json-syntax`: https://marketplace.visualstudio.com/items?itemName=ryanrhee.jinja-json-syntax
