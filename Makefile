SHELL := /bin/bash

FAIR_JSON := $(wildcard data/*.json)

all : check-schema sanitize summary.csv 

check-schema :
	jsonschema`for json in data/*.json; do printf -- " -i %s" $$json; done;` schema/fair.schema.json

sanitize :
# Dereference Wayback Machine links:
	-sed -i 's_https://web.archive.org/web/[[:digit:]]\{14\}/__' $$(grep -RIPl "https://web.archive.org/web/\d{14}/" data | sort) summary.csv
	-sed -i 's_:80/_/_' $$(grep -RIPl ":80/" data | sort) summary.csv

summary.csv : $(FAIR_JSON)
	python/summary.py data/*.json $@

