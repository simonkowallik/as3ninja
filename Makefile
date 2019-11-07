.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . \( -path ./env -o -path ./venv -o -path ./.env -o -path ./.venv \) -prune -o -name '*.egg-info' -exec rm -fr {} +
	find . \( -path ./env -o -path ./venv -o -path ./.env -o -path ./.venv \) -prune -o -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint:
	flake8 as3ninja tests
	pylint as3ninja tests
	mypy as3ninja

black:
	black as3ninja/*.py
	black tests/*.py

isort:
	isort as3ninja/*.py
	isort tests/*.py

code-format: isort black

test: ## run tests quickly with the default Python
	py.test --cov=as3ninja --doctest-modules -ra -v

tests: test

test-all: ## run tests on every Python version with tox
	tox

coverage: ## check code coverage quickly with the default Python
	coverage run --source as3ninja -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/as3ninja.rst
	rm -f docs/modules.rst
	rm -f README.md
	pipenv lock -r > docs/requirements.txt
	pipenv lock -r --dev | tail -n +2 >> docs/requirements.txt
	sphinx-apidoc -o docs/ as3ninja
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	pandoc -f rst -t gfm -o README.md _README.rst
#	$(BROWSER) docs/_build/html/index.html

release: dist ## package and upload a release
	twine upload dist/*
executable:
	pyinstaller --name as3ninja as3ninja/cli.py

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	python setup.py install

dependencies:
	pipenv lock
	pipenv-setup sync
	pipenv lock -r --dev > docs/requirements.txt
