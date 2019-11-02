==============
Templating 101
==============

.. todo:: documentation about: Building AS3 Templates
    - Jinja2 Resouces


Template Configuration Files
----------------------------

.. todo::
    - as3ninja. namespace
    - as3ninja.declaration_template
    - as3ninja.git: information about the git clone operation and repository based on request branch/commit/tag


Declaration Templates
---------------------

.. todo::
    - ninja. namespace: Template Configurations is loaded in here (all variables need to be prefixed with ninja.)
    - special functions and filters
    - reference to jinja2


Git
---
.. todo::
    - as3ninja.git: information about the git clone operation and repository based on request branch/commit/tag
    - as3ninja.git: outline details


.. Note:: Git Authentication is not explicitly handled.

    You could however use the following notation to implicitly provide credentials: ``https://<username>:<password>@gitsite.domain/repository``

    Another option is ``.netrc``, which can be placed in the docker container at ``/as3ninja/.netrc``, see: `confluence.atlassian.com .. Using the .netrc file`_

.. _`confluence.atlassian.com .. Using the .netrc file`: https://confluence.atlassian.com/bitbucketserver/permanently-authenticating-with-git-repositories-776639846.html#PermanentlyauthenticatingwithGitrepositories-Usingthe.netrcfile
