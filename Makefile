.PHONY: install 2L all qa clean

PY := $(shell test -x .venv/bin/python && echo .venv/bin/python || echo python3)

install:
	$(PY) -m pip install -e .
	$(PY) -m playwright install chromium

2L:
	$(PY) -m src.render --questionnaire 2L
	$(PY) -m src.export --questionnaire 2L --format print
	$(PY) -m src.export --questionnaire 2L --format tl

qa:
	$(PY) -m src.qa --questionnaire 2L

all: 2L qa

clean:
	rm -rf output/pdf/* output/tl/* output/qa-reports/*
