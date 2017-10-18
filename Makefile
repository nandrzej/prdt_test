.PHONY: help lint it-test run

help:
	@echo "    lint"
	@echo "        Check code style and formatting."
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

deps:
	pip install -r requirements.txt

test-deps:
	pip install -r requirements_test.txt

it-test: deps test-deps
	py.test

run: deps
	python src/bigquery_tool.py
