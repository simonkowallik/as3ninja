![AS3 Ninja](https://raw.githubusercontent.com/simonkowallik/as3ninja/master/docs/_static/logo.png)

_AS3 Ninja is a templating and validation engine for your AS3 declarations. No matter if you prefer a CLI or Swagger REST API, AS3 Ninja has you covered!_

[![CI Pipeline](https://github.com/simonkowallik/as3ninja/actions/workflows/ci-pipeline.yaml/badge.svg)](https://github.com/simonkowallik/as3ninja/actions/workflows/ci-pipeline.yaml)
[![Documentation Status](https://readthedocs.org/projects/as3ninja/badge/?version=latest&style=flat)](https://as3ninja.readthedocs.io/en/latest/?badge=latest)
[![Maintainability](https://api.codeclimate.com/v1/badges/9f516ff8bde00c7c082d/maintainability)](https://codeclimate.com/github/simonkowallik/as3ninja/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/9f516ff8bde00c7c082d/test_coverage)](https://codeclimate.com/github/simonkowallik/as3ninja/test_coverage)

- Free software: ISC license
- Documentation: <https://as3ninja.readthedocs.io>
- Works with Python 3.8 and up

## What is AS3 Ninja and what can it do for you?

AS3 Ninja is a templating engine as well as a validator for
[AS3](https://github.com/F5Networks/f5-appsvcs-extension/) declarations.
It offers a CLI for local usage, as well as a OpenAPI/Swagger based REST
API.

AS3 Ninja empowers you to create AS3 declarations in a DevOps way by
embracing the ideas of GitOps and CI/CD.

It separates Configuration from Code (Templates) as far as YOU wish.

AS3 Ninja let's you decide to scale between declarative and imperative
paradigms to fit your needs.

What AS3 Ninja doesn't do:

- It does not provide you with a UI to create configurations
- It does not deploy AS3 configurations

## Features

- Validate your AS3 Declarations against the AS3 Schema (via API, eg. for CI/CD) and AS3 specific formats
- Create AS3 Declarations from templates using the full power of Jinja2 (CLI and API)
  - reads your JSON or YAML configurations to generate AS3 Declarations
  - carefully crafted Jinja2 `as3ninja.filters` and `as3ninja.functions` further enhance the templating capabilities
- Use Git(hub) to pull template configurations and declaration templates
- HashiCorp Vault integration to retrieve secrets
- AS3 Ninja provides a simple CLI..
- ..and a REST API including a Swagger/OpenAPI interface at `/api/docs` and `/api/redoc` (openapi.json @ `/api/openapi.json`)

## AS3 Ninja Interface

Some impressions from AS3 Ninja's interfaces:

### the Command Line

![CLI](https://as3ninja.readthedocs.io/en/latest/_images/_cli.svg)

### the API UI

ReDoc and Swagger UI:

![ReDoc](https://raw.githubusercontent.com/simonkowallik/as3ninja/master/docs/_static/_api.gif)

Swagger UI demo:

![Swagger UI](https://raw.githubusercontent.com/simonkowallik/as3ninja/master/docs/_static/_api_demo.gif)

## Disclaimer and Security Note

AS3 Ninja is not a commercial product and [is not covered by any form of support, there is no contract nor SLA!](./docs/support.rst). Please read, understand and adhere to the license before use.

AS3 Ninja's focus is flexibility in templating and features, it is not hardened to run in un-trusted environments.

- It comes with a large set of dependencies, all of them might introduce security issues
- Jinja2 is not using a Sandboxed Environment and the `readfile` filter allows arbitrary file includes.
- The API is unauthenticated

> **_WARNING:_**  Only use AS3 Ninja in a trusted environment with restricted access and trusted input.

## Where to start?

[Read the Docs](https://as3ninja.readthedocs.io/) and then [Try it out](https://as3ninja.readthedocs.io/en/latest/usage.html)\! :-)
