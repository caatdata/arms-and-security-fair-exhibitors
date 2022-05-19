SHELL := /bin/bash

FAIR_JSON := $(wildcard data/*.json)

all : check-schema sanitize summary.csv task

check-schema :
	jsonschema`for json in data/*.json; do printf -- " -i %s" $$json; done;` schema/fair.schema.json

sanitize :
# Dereference Wayback Machine links:
	grep -RIPl "https://web.archive.org/web/\d{14}/" data | xargs -r sed -i 's_https://web.archive.org/web/[[:digit:]]\{14\}/__'
	grep -RIPl ":80/" data | xargs -r sed -i 's_:80/_/_'
	! grep -RIPl '\t' data
	! grep -RIPl '\xa0' data
	! grep -RIPl ' ",?$$' data/
	! grep -RIPl '": " ' data/
	! grep -RIP '[^\\]"",?$$' data/

summary.csv : $(FAIR_JSON)
	python/summary.py data/*.json $@

task :
	python/task.py ignore.csv data/


image/event.png : python/event.geo.json python/plot-map.py python/map.html python/map.js python/map.css
	python/plot-map.py -v python/event.geo.json $@

image/exhibitor.png : python/exhibitor.geo.json python/plot-map.py python/map.html python/map.js python/map.css
	python/plot-map.py -v python/exhibitor.geo.json $@


python/event.jsonl : $(FAIR_JSON) python/event-geojson.jq
	rm -f $@
	jq --indent N -f python/event-geojson.jq $(FAIR_JSON) >> $@

python/event.geo.json : python/event.jsonl
	rm -f $@
	jq -s '{"type": "FeatureCollection", "features": .}' $^ >> $@

python/exhibitor.jsonl : $(FAIR_JSON) python/exhibitor-geojson.jq
	rm -f $@
	jq --indent N -f python/exhibitor-geojson.jq $(FAIR_JSON) >> $@

python/exhibitor.geo.json : python/exhibitor.jsonl
	rm -f $@
	jq -s '{"type": "FeatureCollection", "features": .}' $^ >> $@

