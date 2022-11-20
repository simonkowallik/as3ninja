
============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/simonkowallik/as3ninja/issues.

If you are reporting a bug, please include:

* Your operating system name and version, python version and as3ninja version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

AS3 Ninja could always use more documentation, whether as part of the
official AS3 Ninja docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/simonkowallik/as3ninja/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `as3ninja` for local development.

1. Fork the `as3ninja` repo on GitHub.
2. Clone your fork locally::


.. code-block:: shell

    $ git clone --branch edge git@github.com:your_name_here/as3ninja.git


3. Install your local copy into a virtualenv. Assuming you use poetry::


.. code-block:: shell

    $ cd as3ninja/
    $ poetry shell
    $ poetry install


4. Create a branch for local development::


.. code-block:: shell

    $ git checkout -b (bugfix|feature|enhancement)/name-of-your-bugfix-or-feature


Now you can make your changes locally.

5. When you're done making changes, check that your changes comply to code formatting and pass the tests::


.. code-block:: shell

    $ make lint
    $ make code-format
    $ make test


6. Commit your changes and push your branch to GitHub::


.. code-block:: shell

    $ git add .
    $ git commit
    $ git push origin (bugfix|feature|enhancement)/name-of-your-bugfix-or-feature


7. Submit a pull request through GitHub.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring and update the
   relevant documentation.
3. The pull request should work for Python 3.8 and up. Check
   https://github.com/simonkowallik/as3ninja/actions
   and make sure that the tests pass for all supported Python versions.
