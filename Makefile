.PHONY: install 2L 00 all qa qa-00 clean all-planches publish-2L publish-all deploy

PY := $(shell test -x .venv/bin/python && echo .venv/bin/python || echo python3)

PLANCHES := $(patsubst data/questionnaires/%.json,%,$(wildcard data/questionnaires/*.json))

install:
	$(PY) -m pip install -e .
	$(PY) -m playwright install chromium

# Pattern rule : make 2L, make 00, etc.
2L 00:
	$(PY) -m src.render --questionnaire $@
	$(PY) -m src.export --questionnaire $@ --format print
	$(PY) -m src.export --questionnaire $@ --format tl

qa:
	$(PY) -m src.qa --questionnaire 2L

qa-00:
	$(PY) -m src.qa --questionnaire 00

all-planches:
	@for p in $(PLANCHES); do echo ">> Building $$p"; $(MAKE) $$p; done

all: 2L qa

clean:
	rm -rf output/pdf/* output/tl/* output/qa-reports/*

publish-2L:
	$(PY) -m src.publish --questionnaire 2L

publish-all:
	$(PY) -m src.publish --all

deploy: publish-all
	git add docs/
	git commit -m "Deploy docs/ — $$(date +%Y-%m-%d)"
	git push origin main
