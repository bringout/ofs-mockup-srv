PYTHON ?= python
PORT ?= 8200
UNAVAILABLE ?= false

.PHONY: install-dev run run-available run-unavailable test lint format demo demo-pin demo-invoice

install-dev:
	$(PYTHON) -m pip install -e .[dev]

run:
	ofs-mockup-srv --port $(PORT)

run-available:
	ofs-mockup-srv --available --port $(PORT)

run-unavailable:
	ofs-mockup-srv --unavailable --port $(PORT)

test:
	pytest -q

lint:
	flake8 ofs_mockup_srv/
	mypy ofs_mockup_srv/

format:
	black ofs_mockup_srv/
	isort ofs_mockup_srv/

demo:
	bash scripts/demo_flows.sh all

demo-pin:
	bash scripts/demo_flows.sh pin

demo-invoice:
	bash scripts/demo_flows.sh invoice

