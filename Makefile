.PHONY: help clean clean-build clean-coverage clean-pyc clean-skbuild clear-test lint test test-all coverage docs-only docs release dist

help:
	@echo "$(MAKE) [target]"
	@echo
	@echo "  targets:"
	@echo "    clean       - remove build and testing artifacts"
	@echo "    lint        - check style with flake8"
	@echo "    test        - run tests quickly with the default Python"
	@echo "    test-all    - run tests on every Python version with tox"
	@echo "    coverage    - check code coverage quickly with the default Python"
	@echo "    docs-only   - generate Sphinx HTML documentation, including API docs"
	@echo "    docs        - same as 'docs-only' and load HTML using default web browser"
	@echo "    release     - package and upload a release"
	@echo "    dist        - package"
	@echo

clean: clean-build clean-coverage clean-pyc clean-skbuild clear-test

clean-build:
	rm -fr build/
	rm -fr dist/
	find . -type d -name '*.eggs' -exec rm -rf {} +
	find . -type d -name '*.egg-info' -exec rm -rf {} +
	find . -type f -name 'MANIFEST' -exec rm -f {} +
	find tests/samples/*/dist/ -type d -exec rm -rf {} + > /dev/null 2>&1 || true

clean-coverage:
	rm -fr htmlcov/
	find . -name '.coverage' -exec rm -f {} +
	find . -name 'coverage.xml' -exec rm -f {} +

clean-pyc:
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

clean-skbuild:
	rm -rf _skbuild
	find tests/samples/*/_skbuild/ -type d -exec rm -rf {} + > /dev/null 2>&1 || true

clear-test:
	rm -rf .cache
	rm -rf .pytest_cache/

lint:
	flake8

test:
	python setup.py test

test-all:
	tox

coverage: test
	coverage html
	open htmlcov/index.html || xdg-open htmlcov/index.html

docs-only:
	rm -f docs/skbuild.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ --module-first skbuild
	$(MAKE) -C docs clean
	$(MAKE) -C docs html

docs: docs-only
	open docs/_build/html/index.html || xdg-open docs/_build/html/index.html

release: clean
	python setup.py sdist upload
	python setup.py bdist_wheel upload

dist: clean
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist
