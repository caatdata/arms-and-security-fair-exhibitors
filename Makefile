SHELL := /bin/bash

FAIR_JSON_GLOB := data/*.json
FAIR_JSON := $(wildcard $(FAIR_JSON_GLOB))
TMP_DIR = /tmp/arms-fair-data
TMP = $(TMP_DIR)/tmp
IMAGE_FAIR_DIR = image/fair
IMAGE_TRAVEL_ISO2_LIST := gb
IMAGE_TRAVEL_ISO2_PNG := $(patsubst %,image/iso2.%.travel.png,$(IMAGE_TRAVEL_ISO2_LIST))
# IMAGE_TRAVEL_NAME_LIST := lockheed boeing bae raytheon
# IMAGE_TRAVEL_NAME_PNG := $(patsubst %,image/name.%.travel.png,$(IMAGE_TRAVEL_NAME_LIST))
# IMAGE_TRAVEL_FAIR_PNG := $(patsubst %.json,$(IMAGE_FAIR_DIR)/%.travel.png,$(shell jq -r 'first(.exhibitor[]? | select(.address)) | input_filename | sub("data/"; "")' $(FAIR_JSON)))

.PHONY : image


all : check-schema sanitize summary.csv task

image : $(IMAGE_TRAVEL_ISO2_PNG)
# travel-fair : $(IMAGE_TRAVEL_FAIR_PNG)


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

$(IMAGE_FAIR_DIR) :
	mkdir -p $@


image/event.png : $(TMP_DIR)/event.geo.json tools/map.html tools/map.css tools/heatmap.py tools/heatmap.js
	tools/heatmap.py -v $< $@

image/exhibitor.png : $(TMP_DIR)/exhibitor.geo.json tools/map.html tools/map.css tools/heatmap.py tools/heatmap.js
	tools/heatmap.py -v $< $@

image/iso2.%.travel.png : $(TMP_DIR)/iso2.%.travel.json tools/map.html tools/map.css tools/travel-map.py tools/travel-map.js
	tools/travel-map.py -v $< $@

# image/name.%.travel.png : $(TMP_DIR)/name.%.travel.json tools/map.html tools/map.css tools/travel-map.py tools/travel-map.js
# 	tools/travel-map.py -v $< $@

# $(IMAGE_FAIR_DIR)/%.travel.png : $(TMP_DIR)/%.travel.json $(IMAGE_FAIR_DIR) tools/map.html tools/map.css tools/travel-map.py tools/travel-map.js
# 	tools/travel-map.py -v $< $@




image/category.png : $(TMP_DIR)/category.txt
# Add `--no_collocations` to disable bigrams
	wordcloud_cli --text $^ \
	  --width=1200 --height=600 --margin=15 \
	  --background="#FAFAFA" --color="#E20613" \
	  --imagefile $@


$(TMP_DIR)/iso2.%.travel.json : $(FAIR_JSON) tools/travel.jq $(TMP_DIR)
	rm -f $@
	jq -s --arg iso2 $* -f tools/travel.jq $(FAIR_JSON_GLOB) >> $@

# $(TMP_DIR)/name.%.travel.json : $(FAIR_JSON) tools/travel.jq $(TMP_DIR)
# 	rm -f $@
# 	jq -s --arg name $* -f tools/travel.jq $(FAIR_JSON_GLOB) >> $@

# $(TMP_DIR)/%.travel.json : data/%.json tools/travel.jq $(TMP_DIR)
# 	rm -f $@
# 	jq -s -f tools/travel.jq $< >> $@

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


$(TMP_DIR)/category.txt : tools/category.jq $(FAIR_JSON) 
	rm -f $@
	jq -sr -f $< $(FAIR_JSON_GLOB) >> $@


$(TMP_DIR)/fair.csv : tools/fair-csv.jq $(TMP_DIR) $(FAIR_JSON)
	rm -f $@
	jq -r -f $< <(echo 'null') $(FAIR_JSON_GLOB) >> $@

$(TMP_DIR)/exhibitor.csv : tools/exhibitor-csv.jq $(TMP_DIR) $(FAIR_JSON)
	rm -f $@
	jq -r -f $< <(echo 'null') $(FAIR_JSON_GLOB) >> $@

$(TMP_DIR)/organiser.csv : tools/organiser-csv.jq $(TMP_DIR) $(FAIR_JSON)
	rm -f $@
	jq -r -f $< <(echo 'null') $(FAIR_JSON_GLOB) >> $@

$(TMP_DIR)/arms-fair-data.zip : $(TMP_DIR)/fair.csv $(TMP_DIR)/exhibitor.csv $(TMP_DIR)/organiser.csv
	rm -f $@
	zip -r $@ $^

release : $(TMP_DIR)/arms-fair-data.zip
