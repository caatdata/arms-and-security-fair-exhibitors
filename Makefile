SHELL := /bin/bash

FAIR_JSON_GLOB := data/*.json
FAIR_JSON := $(wildcard $(FAIR_JSON_GLOB))
TMP_DIR = /tmp/arms-fair-data
TMP = $(TMP_DIR)/tmp

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

$(TMP_DIR) :
	mkdir -p $@


image/event.png : $(TMP_DIR)/event.geo.json tools/map.html tools/map.css tools/heatmap.py tools/heatmap.js
	tools/heatmap.py -v $< $@

image/exhibitor.png : $(TMP_DIR)/exhibitor.geo.json tools/map.html tools/map.css tools/heatmap.py tools/heatmap.js
	tools/heatmap.py -v $< $@

image/travel-gb.png : $(TMP_DIR)/travel-gb.json tools/map.html tools/map.css tools/travel-map.py tools/travel-map.js
	tools/travel-map.py -v $< $@

image/category.png : $(TMP_DIR)/category.txt
# Add `--no_collocations` to disable bigrams
	wordcloud_cli --text $^ \
	  --width=1200 --height=600 --margin=15 \
	  --background="#FAFAFA" --color="#E20613" \
	  --imagefile $@


$(TMP_DIR)/event.jsonl : tools/event-geojson.jq $(TMP_DIR) $(FAIR_JSON) 
	rm -f $@
	jq --indent N -f $< $(FAIR_JSON_GLOB) >> $@

$(TMP_DIR)/event.geo.json : $(TMP_DIR)/event.jsonl
	rm -f $@
	jq -s '{"type": "FeatureCollection", "features": .}' $^ >> $@

$(TMP_DIR)/exhibitor.jsonl : tools/exhibitor-geojson.jq $(TMP_DIR) $(FAIR_JSON)
	rm -f $@
	jq --indent N -f $< $(FAIR_JSON_GLOB) >> $@

$(TMP_DIR)/exhibitor.geo.json : $(TMP_DIR)/exhibitor.jsonl
	rm -f $@
	jq -s '{"type": "FeatureCollection", "features": .}' $^ >> $@

$(TMP_DIR)/travel-gb.json : tools/travel.jq $(TMP_DIR) $(FAIR_JSON)
	rm -f $@
	jq -fs --arg iso2 GB $< $(FAIR_JSON_GLOB) >> $@


$(TMP_DIR)/category.txt : tools/category.jq $(FAIR_JSON) 
	rm -f $@
	jq -sr -f $< $(FAIR_JSON_GLOB) >> $@


