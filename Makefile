.PHONY: deps install test lint clean

deps:
	$(info [+] Installing required Python modules)
	@pip install -r requirements.txt

install: deps

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