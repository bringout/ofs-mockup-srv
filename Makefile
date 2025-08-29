PYTHON ?= python
PORT ?= 8200
GSC ?= 9999

.PHONY: install-dev run run-gsc test lint format demo demo-pin demo-invoice

install-dev:
	$(PYTHON) -m pip install -e .[dev]

run:
	ofs-mockup-srv --port $(PORT)

run-gsc:
	ofs-mockup-srv --gsc $(GSC) --port $(PORT)

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

