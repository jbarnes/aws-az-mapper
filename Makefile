.PHONY: deps map

deps:
	$(info [+] Installing required Python modules)
	@pip install -r requirements.txt

map:
	$(info [+] Starting Availability Zone mapping tool)
	@python3 src/az_mapper.py