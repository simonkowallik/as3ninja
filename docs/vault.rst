=================
Vault Integration
=================

`HashiCorp Vault`_ is a reliable and secure secret management engine widely used in the DevOps community.

.. _`HashiCorp Vault`: https://www.vaultproject.io

The integration in AS3 Ninja is based on `hvac`_.

.. _`hvac`: https://github.com/hvac/hvac

Background
----------
The term `secrets` describes secret information, like private cryptographic keys for x509 certificates, passwords and other shared secrets.
As secrets are often used to ensure confidentiality and integrity, it is crucial to prevent compromise.
Configuration management and version control systems, like git(hub), are not well suited nor meant to hold secret information.
HashiCorp Vault provides a solution to manage secrets for AS3 Ninja.

Different types of secrets exist, therefore Vault provides a variety of `Secrets Engines` to fullfil the specific needs of these secret types.
Two `Secrets Engines` are useful particular for AS3 Ninja:

* KV1
* KV2

Both are Key Value stores, where KV2 provides versioning of secrets.
See `Vault Docs: Secrets Engines: Key/Value`_ for more details.

.. _`Vault Docs: Secrets Engines: Key/Value`: https://www.vaultproject.io/docs/secrets/kv/index.html

Concept
-------
AS3 Ninja is a client to Vault and retrieves secrets during AS3 Declaration generation.
Although secrets management is a complicated topic the AS3 Ninja Vault integration is relatively straightforward.
One important assumption is that the authentication to Vault is not performed directly by AS3 Ninja.
Also see `Vault Docs: Concepts: Authentication`_.

.. _`Vault Docs: Concepts: Authentication`: https://www.vaultproject.io/docs/concepts/auth.html

AS3 Ninja assumes that a `token` is provided, which represents an authenticated session to communicate with Vault. Generating/Fetching the token is out of scope of AS3 Ninja.

AS3 Ninja can also communicate to multiple Vault instances in case secrets are spread across different Vault deployments.


Vault Communication
-------------------
Communication with Vault is established through Vault's REST API.

To initiate communication a three parameters are required:

1. Vault's address
2. communication parameters
3. A valid token

There are multiple ways to specify these parameters depending on how you use the Vault integration.

Vault can be accessed with :py:mod:`as3ninja.vault.vault`, which is available as Jinja2 filter as well as a Jinja2 function.

A specific `client` can be created using the Jinja2 function :py:mod:`as3ninja.vault.VaultClient`.
This `client` is tied to the Vault instance defined by the parameters passed to `VaultClient`.
The `vault` filter/function optionally accepts this `client` as a parameter.

This is helpful in case a specific Vault instance must be contacted or multiple Vault instances are needed.

The usage of `vault` and `VaultClient` is explained later.

When using `vault` and not passing a specific `client`, AS3 Ninja will use the :py:meth:`as3ninja.vault.VaultClient.defaultClient` to initiate communication with Vault.
The `defaultClient` connection logic is as follows:

1. It will first check if an authenticated vault connection exists already.

    This is helpful in case AS3 Ninja is executed from the command line and a Vault connection has been established using Vaults own cli.

2. If 1. isn't successful It will then check the Jinja2 Context for the namespace ``ninja.as3ninja.vault`` and use ``addr``, ``token`` and ``ssl_verify`` for connection establishment

    This provides great flexibility as the Vault connection can be parametrized by the Template Configuration.

3. For any namespace variable in 2., it will check the environment variables ``VAULT_ADDR``, ``VAULT_TOKEN`` and ``VAULT_SKIP_VERIFY``.

    This allows to fallback to environment variables. This is helpful when AS3 Ninja is used through the cli.
    It is also very helpful when AS3 Ninja runs as a docker container as the default Vault connection can be specified on the container level.

4. If ``VAULT_SKIP_VERIFY`` doesn't exist, it will use ``VAULT_SSL_VERIFY`` from the AS3 Ninja configuration file (``as3ninja.settings.json``).


The variables in ``ninja.as3ninja.vault`` can be specified using the Template Configuration, for example:

.. code-block:: yaml

    as3ninja:
      vault:
        addr: https://192.0.2.100:8201
        token: s.jbm5eO3rmh1kxrraNA9Q0N5r
        ssl_verify: false

.. Note:: Remember that anything defined in the Template Configuration will be stored in the ``ninja`` namespace within the Jinja2 context. That's why ``ninja.as3ninja.vault`` is used but the YAML example starts by defining ``as3ninja:``.


Referencing Secrets in Template Configurations
----------------------------------------------
To retrieve a secret from Vault a couple of parameters are required:

1. The `mount_point` of the Secrets Engine
2. The `path` of the Secret
3. The Secrets `engine`
4. The `version` (in case of Secrets Engine kv2)
5. The `filter` selects the exact piece of information required from the response

mount_point
***********
If the `mount_point` is part of the `path` and is configured during setup of the Secrets `engine` in Vault.
If the `mount_point` is just one level, for example `/mySecretEngineKV2`, it can be omitted if it is part of `path`.

path
****
The `path` defines which secret to retrieve. If `mount_point` is omitted is must include the `mount_point`, see paragraph above.

engine
******
`engine` defines the Secrets Engine the secret is stored in.
Default is KV2.

Supported Secrets Engines:

* KV1
* KV2

version
*******
In case KV2 is used, secrets can be versioned.
When `version` is provided, a specific version of the secret is fetched.
Default is `version=0`, which is the most recent version.
`version` is optional.

filter
******

`filter` is an optional setting and can be used to select a specific element from the Vault response.
The filter is a string of keys separated by dots (e.g. `key1.key2.key3`).
If a key contains a dot in the name, it can be escaped (e.g. `k\\\\.e\\\\.y.anotherKey` would be split to `k.e.y` and `anotherKey`).

Examples
********

.. code-block:: yaml

    secrets:
      myWebApp:
        path: /secretkv2/myWebApp/privateKey

The simplest definition of a secret just contains the path.
`vault` will use the KV2 secrets `engine` and return the most recent `version` of the secret.

.. code-block:: yaml

    secrets:
      myAPI:
        path: /secretOne/myAPI/sharedKey
        engine: kv1

When using KV1, the `engine` must be explicitly specified.

.. code-block:: yaml

    secrets:
      v1Service:
        path: /otherService/privateKey
        mount_point: /SecEnginePath/myKV2
        version: 1
      latestService:
        path: /otherService/privateKey
        mount_point: /SecEnginePath/myKV2

Say a secrets engine was created with:
``vault secrets enable -path=/SecEnginePath/myKV2 kv-v2``

As the path has multiple levels, the `mount_point` must be explicitly specified.

The secret `v1Service` references to a specific version of the secret (`version: 1`), where `latestService` refers to the most recent version.
`latestService` could have used `version: 0` to explicitly state that the most recent version should be used but this is optional.


Using Vault with AS3 Ninja
--------------------------

Let's look at using `vault` as a jinja2 filter and function as well as using `VaultClient`.

.. Note:: To keep the examples concise, none of the below produce a valid AS3 declaration. Therefore the `--no-validate` flag is required.

A simple example (Secrets Engine: KV1)
**************************************

.. code-block:: yaml
    :linenos:

    # Template Configuration
    secrets:
      myAPI:
        path: /secretOne/myAPI/sharedKey
        engine: kv1

Our secret will be accessible during transformation of the Declaration Template as ``ninja.secrets.myAPI``.
``ninja.secrets.myAPI.path`` will refer to the value ``/secretOne/myAPI/sharedKey`` and ``ninja.secrets.myAPI.engine`` will refer to ``kv1``.

.. code-block:: jinja
    :linenos:

    {# Declaration Template #}
    {
      "myAPI": {{ ninja.secrets.myAPI | vault | jsonify }}
    }

We use `vault` as a filter and the value of ``ninja.secrets.myAPI`` is passed as the first parameter automatically by jinja2.
``vault`` will read all keys in the passed parameter and try to retrieve the relevant secret from Vault.

Run as3ninja:

.. code-block:: shell

    as3ninja transform -c ninja.yml -t template.j2 --no-validate | jq .

Resulting JSON:

.. code-block:: json
    :linenos:
    :emphasize-lines: 8

    {
      "myAPI": {
        "request_id": "308c8b5c-fadc-ff32-8543-ad611fc53d72",
        "lease_id": "",
        "renewable": false,
        "lease_duration": 2764800,
        "data": {
          "secretKey": "AES 128 4d3642df883756b0d5746f32463f6005"
        },
        "wrap_info": null,
        "warnings": null,
        "auth": null
      }
    }

The value of ``"myAPI"`` contains details about the fetched Vault secret, probably more than needed. Likely we are only interested in a specific value, for example `data -> secretKey`.
Modifying the Declaration Template like below would just extract this specific value:

.. code-block:: jinja
    :linenos:

    {
      "myAPI": {{ (ninja.secrets.myAPI | vault)['data']['secretKey'] | jsonify }}
    }


Using a `filter` in the secret's definition within the Template Configuration is a better alternative as this separates the configuration further from the implementation (the Declaration Template).
Here is the updated Template Configuration:

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 6

    # Template Configuration
    secrets:
      myAPI:
        path: /secretOne/myAPI/sharedKey
        engine: kv1
        filter: data.secretKey


The resulting JSON now only contains the information we are looking for:

.. code-block:: json
    :linenos:
    :emphasize-lines: 2

    {
      "myAPI": "AES 128 4d3642df883756b0d5746f32463f6005"
    }


Example using Secrets Engine KV2
********************************

.. code-block:: yaml
    :linenos:

      # Template Configuration
      latestService:
        path: /otherService/privateKey
        mount_point: /SecEnginePath/myKV2


.. code-block:: jinja
    :linenos:

    {# Declaration Template #}
    {
      "latestService": {{ ninja.secrets.latestService | vault | jsonify }}
    }

Run as3ninja:

.. code-block:: shell

    as3ninja transform -c ninja.yml -t template.j2 --no-validate | jq .

Resulting JSON:

.. code-block:: json
    :linenos:
    :emphasize-lines: 7,8,9,11,15

    {
      "latestService": {
        "request_id": "25b2debe-7514-de9a-8beb-dd798f898ddf",
        "lease_id": "",
        "renewable": false,
        "lease_duration": 0,
        "data": {
          "data": {
            "privateKey": "-----BEGIN RSA PRIVATE KEY-----\nMIHzAgEAAjEAvAI1w37cQcrflizN6Qa6GYVO26Sup5J0WWirYDS1aoxXCjQDcN4Q\nf7cCQ82kSzcjAgMBAAECMFS5sjzdiKjlogjtPAYNkAQ8PSNifYrqxlpT4D5+TpWj\nM1ODUjTVZBPQXuUIJYo6gQIZAOBcs33j5C6k7sisCVAvJTCTmdMx037zYQIZANaF\nLSMLGaEhYz1da3OR6IHyM9Anx/h9AwIZAL4vlq+GeKzZfth4jMR90malF+Yg/IlG\nwQIZAJKgRqDMRoFfK9DW2MoOsgiX/xhJCKLs9wIYPHBqLjhfB5Ycuk+WyxHj2uNQ\nNpf7zbsE\n-----END RSA PRIVATE KEY-----"
          },
          "metadata": {
            "created_time": "2019-11-30T13:05:16.5110593Z",
            "deletion_time": "",
            "destroyed": false,
            "version": 2
          }
        },
        "wrap_info": null,
        "warnings": null,
        "auth": null
      }
    }

As we already know the result carries likely more information than we need. In contrast to KV1 the KV2 Secrets Engine uses one more level of nesting as it does provide explicit metadata (line 11) about the secret.
The information we are looking for is found at `data -> data -> privateKey` (line 7-9). Within the secret's metadata the version of the retrieved secret is displayed (``"version": 2`` at line 15).

As we already learnt we can filter the response data by either updating the Declaration Template or using the filter.
Updated Template Configuration:


.. code-block:: yaml
    :linenos:
    :emphasize-lines: 5

      # Template Configuration
      latestService:
        path: /otherService/privateKey
        mount_point: /SecEnginePath/myKV2
        filter: data.privateKey

.. Note:: Although KV2 stores the `privateKey` in `data -> data` we can omit the first instance of `data` as this is automatically prepended by the vault jinja2 filter/function. If you would like to access the `version` in the `metadata` the filter would be `metadata.version`.


Result:

.. code-block:: json

    {
      "latestService": "-----BEGIN RSA PRIVATE KEY-----\nMIHzAgEAAjEAvAI1w37cQcrflizN6Qa6GYVO26Sup5J0WWirYDS1aoxXCjQDcN4Q\nf7cCQ82kSzcjAgMBAAECMFS5sjzdiKjlogjtPAYNkAQ8PSNifYrqxlpT4D5+TpWj\nM1ODUjTVZBPQXuUIJYo6gQIZAOBcs33j5C6k7sisCVAvJTCTmdMx037zYQIZANaF\nLSMLGaEhYz1da3OR6IHyM9Anx/h9AwIZAL4vlq+GeKzZfth4jMR90malF+Yg/IlG\nwQIZAJKgRqDMRoFfK9DW2MoOsgiX/xhJCKLs9wIYPHBqLjhfB5Ycuk+WyxHj2uNQ\nNpf7zbsE\n-----END RSA PRIVATE KEY-----"
    }


Using `vault` as a jinja2 function
**********************************

.. Note:: The below example is based on the KV2 example above

We can use `vault` as a jinja2 function as well.
This allows us to implement more generic queries and re-use the secret information without asking Vault all the time.

.. code-block:: jinja
    :linenos:
    :emphasize-lines: 3

    {
    {% set s = namespace() %}
    {% set s.latestService = vault(secret=ninja.secrets.latestService, filter="") %}
    {% set s.latestService_privKey = s.latestService['data']['data']['privateKey'] %}
    {% set s.latestService_ver = s.latestService['data']['metadata']['version'] %}
        "latestService_privateKey": {{ s.latestService_privKey | jsonify }},
        "latestService_version": {{ s.latestService_ver | jsonify }}
    }

The above Declaration Template creates a jinja2 variable namespace for better reusability.
`vault` is invoked passing ``ninja.secrets.latestService`` to the `secret` parameter manually. When using `vault` as a jinja2 filter, this isn't necessary as the "piped" variable name is passed to the `secret` parameter automatically.
In addition the `filter` parameter is set to an empty string to override any `filter` set within the Template Configuration. The empty string is not treated as a filter, therefore the whole secret is returned.

``secrets.latestService`` now contains all the data we saw in the previous example and we create two more variables to store and later use the specific secret information we are interested in.

The resulting JSON looks like this:

.. code-block:: json
    :linenos:

    {
      "latestService_privateKey": "-----BEGIN RSA PRIVATE KEY-----\nMIHzAgEAAjEAvAI1w37cQcrflizN6Qa6GYVO26Sup5J0WWirYDS1aoxXCjQDcN4Q\nf7cCQ82kSzcjAgMBAAECMFS5sjzdiKjlogjtPAYNkAQ8PSNifYrqxlpT4D5+TpWj\nM1ODUjTVZBPQXuUIJYo6gQIZAOBcs33j5C6k7sisCVAvJTCTmdMx037zYQIZANaF\nLSMLGaEhYz1da3OR6IHyM9Anx/h9AwIZAL4vlq+GeKzZfth4jMR90malF+Yg/IlG\nwQIZAJKgRqDMRoFfK9DW2MoOsgiX/xhJCKLs9wIYPHBqLjhfB5Ycuk+WyxHj2uNQ\nNpf7zbsE\n-----END RSA PRIVATE KEY-----",
      "latestService_version": 2
    }

Specifying a secret version
***************************

A secret version can be specified either in the secrets configuration statement or explicitly via `vault`'s ``version`` parameter.

If we modify the `vault` call from the previous example like below, version 1 of the secret will be retrieved.
The ``version`` parameter is optional and overrules any version configuration. It is valid regardless if `vault` is used as a filter or function.

.. code-block:: jinja
    :linenos:
    :emphasize-lines: 1

    {% set secrets.latestService = vault(secret=ninja.secrets.latestService,version=1) %}

.. code-block:: json
    :linenos:

    {
      "latestService_privateKey": "-----BEGIN RSA PRIVATE KEY-----\nMIGrAgEAAiEAyKNcibrMfVxuEwtifphGvEH1eP5Gjb3jbq8o0NfjjAMCAwEAAQIg\nRp5RJN0NupX83FEmgr5gLqSYKeiIFCF4/vEcLrvVhOkCEQD5WC8HQPmQLFU//171\n92OVAhEAzf5bxQk73WWXG6Wzcy7LNwIRANUDlQmpZIralOnbjJCtDBECECmOR6sf\nKsGGLg64xdPVu88CEQDrfrKtfD5cSVENuhJ1LLie\n-----END RSA PRIVATE KEY-----",
      "latestService_version": 1
    }

Using VaultClient
*****************

:py:mod:`as3ninja.vault.VaultClient` provides a way to connect to a specific Vault instance explicitly.
`VaultClient` will return a `client` which can be passed to the `vault` filter/function.

Re-using the `myAPI` example with the following Declaration Template:

.. code-block:: jinja
    :linenos:
    :emphasize-lines: 3,5

    {
    {% set vc = namespace() %}
    {% set vc.client = VaultClient(addr="https://localhost:8201", verify=False) %}
    "myAPI": {{
            ninja.secrets.myAPI | vault(client=vc.client) | jsonify
        }}
    }

In this example the `client` is created on line 3 and stored in ``vc.client``, which is then used in the `vault` filter as an argument to the `client` parameter.
No explicit `token` was specified in this example. If no `token` is specified `VaultClient` will try to use the environment variable ``VAULT_TOKEN`` or an existing authenticated session based on Vault's cli (in that order).

An explicit `token` can be specified via the `VaultClient` ``token`` parameter.

Here is a fully parametrized example.

.. code-block:: yaml
    :linenos:

    # Template Configuration
    dev:
      vault:
        token: s.iorspPP7f7EFpyudye6DB6Jn
        server_url: "https://dev-vault.example.net:8200"
        verify: false
    secrets:
      myAPI:
        path: /secretOne/myAPI/sharedKey
        engine: kv1
        filter: data.secretKey

.. code-block:: jinja
    :linenos:
    :emphasize-lines: 3

    {# Declaration Template #}
    {
    {% set vc = namespace() %}
    {% set vc.client = VaultClient(
                          addr=ninja.dev.vault.server_url,
                          token=ninja.dev.vault.token,
                          verify=ninja.dev.vault.verify
                          )
    %}
    "myAPI": {{
            ninja.secrets.myAPI | vault(client=vc.client) | jsonify
        }}
    }


Using the AS3 Ninja vault integration directly with python
----------------------------------------------------------

Although it is out of scope AS3 Ninja's vault integration can be used from python directly.

.. code-block:: python
    :linenos:

    from as3ninja.vault import VaultClient, vault

    my_vault_token = "s.tCU2wabNVCcySNncK2Mf6dwT"

    s_myAPI = {
          'path':'/secretOne/myAPI/sharedKey',
          'engine':'kv1',
          'filter':'data.secretKey',
          }

    s_latestService = {
          'path':'/otherService/privateKey',
          'mount_point':'SecEnginePath/myKV2',
          'filter':'data.privateKey',
        }

    # using vault with an explicit Vault client

    vc = VaultClient(addr="http://localhost:8200/",token=my_vault_token)

    vault(ctx={}, client=vc, secret=s_myAPI)
    'AES 128 4d3642df883756b0d5746f32463f6005'

    vault(ctx={} ,client=vc, secret=s_latestService)['data']['data']['privateKey']
    '-----BEGIN RSA PRIVATE KEY-----\nMIHzAgEAAjEAvAI1w37cQcrflizN6Q...'


    # using vault with a mocked jinja2 context

    vault_settings = {'addr':'http://localhost:8200', 'token':my_vault_token}

    jinja2_context = {'ninja':{'as3ninja':{ 'vault': vault_settings }}}

    vault(ctx=jinja2_context, secret=s_myAPI)
    'AES 128 4d3642df883756b0d5746f32463f6005'

    vault(ctx=jinja2_context, secret=s_latestService)
    '-----BEGIN RSA PRIVATE KEY-----\nMIHzAgEAAjEAvAI1w37cQcrflizN6Q...'

    vault(ctx=jinja2_context, secret=s_latestService, version=1)
    '-----BEGIN RSA PRIVATE KEY-----\nMIGrAgEAAiEAyKNcibrMfVxuEwtifp...'
