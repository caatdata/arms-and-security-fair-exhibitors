SHELL := /bin/bash

FAIR_JSON := $(wildcard data/*.json)

all : check-schema sanitize summary.csv

check-schema :
	jsonschema`for json in data/*.json; do printf -- " -i %s" $$json; done;` schema/fair.schema.json

sanitize :
# Dereference Wayback Machine links:
	grep -RIPl "https://web.archive.org/web/\d{14}/" data | xargs -r sed -i 's_https://web.archive.org/web/[[:digit:]]\{14\}/__'
	grep -RIPl ":80/" data | xargs -r sed -i 's_:80/_/_'

summary.csv : $(FAIR_JSON)
	python/summary.py data/*.json $@

tasks :
	python/task.py ignore.csv data/
