SHELL := /bin/bash

FAIR_JSON_GLOB := data/*.json
FAIR_JSON := $(wildcard $(FAIR_JSON_GLOB))

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
	tools/summary.py data/*.json $@

task :
	tools/task.py ignore.csv data/


image/event.png : tools/event.geo.json tools/plot-map.py tools/map.html tools/map.js tools/map.css
	tools/plot-map.py -v tools/event.geo.json $@

image/exhibitor.png : tools/exhibitor.geo.json tools/plot-map.py tools/map.html tools/map.js tools/map.css
	tools/plot-map.py -v tools/exhibitor.geo.json $@


tools/event.jsonl : $(FAIR_JSON) tools/event-geojson.jq
	rm -f $@
	jq --indent N -f tools/event-geojson.jq $(FAIR_JSON_GLOB) >> $@

tools/event.geo.json : tools/event.jsonl
	rm -f $@
	jq -s '{"type": "FeatureCollection", "features": .}' $^ >> $@

tools/exhibitor.jsonl : $(FAIR_JSON) tools/exhibitor-geojson.jq
	rm -f $@
	jq --indent N -f tools/exhibitor-geojson.jq $(FAIR_JSON_GLOB) >> $@

tools/exhibitor.geo.json : tools/exhibitor.jsonl
	rm -f $@
	jq -s '{"type": "FeatureCollection", "features": .}' $^ >> $@


tools/category.txt : $(FAIR_JSON) tools/category.jq
	rm -f $@
	jq -sr -f tools/category.jq $(FAIR_JSON_GLOB) >> $@

image/category.png : tools/category.txt
# Add `--no_collocations` to disable bigrams
	wordcloud_cli --text $^ \
	  --width=1200 --height=600 --margin=15 \
	  --background="#FAFAFA" --color="#E20613" \
	  --imagefile $@

