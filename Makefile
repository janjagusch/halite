clean:
	@echo "Cleaning up ..."
	@find . -type f -name "*.py[co]" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} +
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +

test_missing_init:
	@echo "Testing for missing __init__.py ..."
	@poetry run python bin/test_missing_init.py

test_tox: test_missing_init
	@echo "Tox testing ..."
	@poetry run tox

test: test_tox clean

format_black:
	@echo "Black formatting ..."
	@poetry run black .

format_prettier:
	@echo "Prettier formatting ..."
	@npx prettier --write $$(find \( -name "*.yml" -o -name "*.yaml" -o -name "*.json" \) -not \( -path "./.venv/*" -o -path "./.tox/*" \))

format: format_black format_prettier clean

lint_black:
	@echo "Black linting ..."
	@poetry run black --check .

lint_prettier:
	@echo "Prettier linting ..."
	@npx prettier --check $$(find \( -name "*.yml" -o -name "*.yaml" -o -name "*.json" \) -not \( -path "./.venv/*" -o -path "./.tox/*" \))

lint_pylint:
	@echo "Pylint linting ..."
	@poetry run pylint halite/
	@poetry run pylint $$(find tests/ -iname "*.py")
	@poetry run pylint $$(find bin/ -iname "*.py")

lint: lint_black lint_prettier lint_pylint clean


standalone_submission:
	@echo "Building submission_standalone.py ..."
	@poetry run bin/build_submission_standalone
	@make format

validate_submission:
	@echo "Validating submission_standalone.py ..."
	@poetry run python bin/validate_submission.py
