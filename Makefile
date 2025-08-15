# Makefile

.PHONY: help setup format lint security pre-commit-all

# Show help for each target
help:
	@echo ""
	@echo "InfraBox Makefile Commands:"
	@echo "---------------------------"
	@echo "setup           Install Python tools and Git pre-commit hooks"
	@echo "format          Format code using Black"
	@echo "lint            Run static code analysis using Ruff"
	@echo "security        Scan for security issues using Bandit"
	@echo "test            Run unit and integration tests using pytest"
	@echo "coverage        Generate coverage reports for the CLI"
	@echo "check           Run format, lint, and security checks (all-in-one)"
	@echo "pre-commit-all  Run all configured pre-commit hooks across the codebase"
	@echo ""

# Setup Python tools and Git pre-commit hooks
setup:
	pip3 install --upgrade pip
	pip3 install -r requirements.txt
	python3 -m pre_commit install

# Format code using Black
format:
	python3 -m black infrabox.py cli/ tests/

# Run lint checks
lint:
	python3 -m ruff check --fix infrabox.py cli/ tests/
	python3 -m ruff check --show-files infrabox.py cli/ tests/

# Run security scan
security:
	python3 -m bandit -r infrabox.py cli/
	python3 -m bandit -r tests/ -s B101

# Run unit and integration tests
test:
	python3 -m pytest tests/unit
	python3 -m pytest tests/integration

# Run coverage reports
coverage:
	python3 -m pytest --cov=cli --cov-report=term-missing --cov-report=html tests/

# Run full check
check: format lint security test coverage
	@echo "All checks passed successfully!"

# Run all pre-commit hooks against the entire codebase
pre-commit-all:
	python3 -m pre_commit run --all-files
