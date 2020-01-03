==================
AS3 Ninja Settings
==================

``as3ninja.settings.json`` holds the default configuration settings for AS3 Ninja.

AS3 Ninja looks for ``as3ninja.settings.json`` in the following files and uses the first it finds:

1. ``$CWD/as3ninja.settings.json``
2. ``$HOME/.as3ninja/as3ninja.settings.json``

If none of the configuration files exist, it creates ``$HOME/.as3ninja/as3ninja.settings.json`` and writes the current configuration (default + settings overwritten by ENV vars).

Any setting can be overwritten using environment variables. The ENV variable has to be prefixed by ``AS3N_``.
The environment variables take precedence over any setting in the configuration file.

For specific settings and its meaning check the source of :py:mod:`as3ninja.settings.NinjaSettings`.
