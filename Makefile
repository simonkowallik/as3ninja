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
	rm -f .coverage
	rm -f coverage.xml
	rm -fr htmlcov/
	rm -fr .pytest_cache
	find . -name '.mypy_cache' -exec rm -fr {} +

lint:
	pylint as3ninja tests
	mypy as3ninja

black:
	black as3ninja/*.py
	black tests/*.py

isort:
	isort as3ninja/*.py
	isort tests/*.py

code-format: isort black

test:
	tests/run_tests.sh

tests: test

test-docker:
	DOCKER_TESTING=true tests/run_tests.sh

docker-test: test-docker

coverage:
	REPORT=true tests/run_tests.sh
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

## generate Sphinx HTML documentation, including API docs
docs:
	rm -f docs/as3ninja.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ as3ninja
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

dependencies-update:
	poetry update

dependencies-lock:  # lock dependencies and generate requirements.txt
	# requirements.txt, used by: readthedocs, snyk, Dockerfile
	poetry lock
	poetry export --dev --without-hashes \
				-f requirements.txt \
				-o docs/requirements.txt

dependencies: dependencies-update dependencies-lock

publish-testpypi: docs dist
	#poetry config repositories.testpypi https://test.pypi.org/legacy/
	poetry publish -r testpypi

#release: dist ## package and upload a release
#	twine upload dist/*
#executable:
#	pyinstaller --name as3ninja as3ninja/cli.py

dist: clean ## builds source and wheel package
	poetry build
	ls -l dist
