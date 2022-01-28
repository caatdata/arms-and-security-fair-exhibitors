SHELL := /bin/bash

FAIR_JSON := $(wildcard data/*.json)

all : summary.csv check-schema

check-schema :
	jsonschema`for json in data/*.json; do printf -- " -i %s" $$json; done;` schema/fair.schema.json

summary.csv : $(FAIR_JSON)
	python/summary.py data/*.json $@

