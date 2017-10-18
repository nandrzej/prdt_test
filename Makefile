.PHONY: help lint venv deps test-deps it-test run

help:
	@echo "    lint"
	@echo "        Check code style and formatting."
	@echo "    venv"
	@echo "        Creates and activates virtual environment"
	@echo "    deps"
	@echo "        Synchronize requirements"
	@echo "    test-deps"
	@echo "        Synchronize test requirements"
	@echo "    it-test"
	@echo "        Run the integration test (requires internet connection and Google Cloud credentials set up)."
	@echo "    run"
	@echo "        run the tool."

lint:
	flake8 src tests

venv:
	python3 -m venv env
	source env/bin/activate

deps:
	pip install -r requirements.txt

test-deps:
	pip install -r requirements_test.txt

it-test: venv deps test-deps
	py.test

run:
	python src/run_queries.py
