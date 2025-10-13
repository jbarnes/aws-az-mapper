.PHONY: deps install test lint clean help

deps:
	$(info [+] Installing required Python modules)
	@pip install -r requirements.txt

install:
	$(info [+] Installing development dependencies)
	@pip install -r requirements-dev.txt

test:
	$(info [+] Running tests)
	@python3 -m pytest tests/ -v

lint:
	$(info [+] Running pylint)
	@pylint az_mapper.py

clean:
	$(info [+] Cleaning Python artifacts)
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

help:
	@echo "Available targets:"
	@echo "  make install    - Install development dependencies"
	@echo "  make deps       - Install production dependencies"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run pylint"
	@echo "  make clean      - Remove Python artifacts and cache"