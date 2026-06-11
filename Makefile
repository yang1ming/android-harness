.PHONY: check test compile

PYTHON ?= python3

check: test compile

test:
	$(PYTHON) -m pytest

compile:
	$(PYTHON) -m compileall src tests plugins agent-workspace
