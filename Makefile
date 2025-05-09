SHELL := /bin/bash

FAIR_JSON_GLOB := data/*.json
FAIR_JSON := $(wildcard $(FAIR_JSON_GLOB))
FAIR_VALID := $(patsubst data/%.json,.valid/%,$(FAIR_JSON))
TMP_DIR = /tmp/arms-fair-data
TMP = $(TMP_DIR)/tmp
IMAGE_FAIR_DIR = image/fair
IMAGE_TRAVEL_ISO2_LIST := gb
IMAGE_TRAVEL_ISO2_PNG := $(patsubst %,image/iso2.%.exhibitor-travel.png,$(IMAGE_TRAVEL_ISO2_LIST))
MAP_ASSETS := tools/map.html tools/map.css tools/map.js tools/map.py
VENV := .venv


.PHONY : image


all : validate summary.csv task

image : $(IMAGE_TRAVEL_ISO2_PNG)
# travel-fair : $(IMAGE_TRAVEL_FAIR_PNG)


validate : $(FAIR_VALID)

python : $(VENV)
	$(VENV)/bin/pip install -r tools/requirements.txt

$(VENV) :
	virtualenv $@

.valid/% : data/%.json
	mkdir -p .valid
	$(VENV)/bin/check-jsonschema --schemafile schema/fair.schema.json $^
# Dereference Wayback Machine links:
	grep -RIPl "https://web.archive.org/web/\d{14}/" $^ | xargs -r sed -i 's_https://web.archive.org/web/[[:digit:]]\{14\}/__'
	grep -RIPl ":80/" $^ | xargs -r sed -i 's_:80/_/_'
	! grep -RIPl '\t' $^
	! grep -RIPl '\xa0' $^
	! grep -RIPl ' ",?$$' $^
	! grep -RIPl '": " ' $^
	! grep -RIP '[^\\]"",?$$' $^
	touch $@


summary.csv : $(FAIR_JSON)
	$(VENV)/bin/python tools/summary.py data/*.json $@

task :
	$(VENV)/bin/python tools/task.py ignore.csv data/

release : $(TMP_DIR)/arms-fair-data.zip

list-fair-address-country : $(FAIR_JSON) tools/fair-address-country.jq
	jq -sr -f tools/fair-address-country.jq $(FAIR_JSON_GLOB)


$(TMP_DIR) :
	mkdir -p $@

$(IMAGE_FAIR_DIR) :
	mkdir -p $@


images: \
	image/event.png \
	image/exhibitor.png \
	image/category.png \
	image/iso2.gb.exhibitor-travel.png \


$(TMP_DIR)/event.jsonl : tools/event-geojson.jq $(TMP_DIR) $(FAIR_JSON) 
	rm -f $@
	jq --indent N -f $< $(FAIR_JSON_GLOB) >> $@

$(TMP_DIR)/event.geo.json : $(TMP_DIR)/event.jsonl
	rm -f $@
	jq -s '{"type": "FeatureCollection", "features": .}' $^ >> $@

image/event.png : $(TMP_DIR)/event.geo.json $(MAP_ASSETS) tools/heatmap.js
	$(VENV)/bin/python tools/map.py -v -j heatmap.js $< $@


$(TMP_DIR)/exhibitor.jsonl : tools/exhibitor-geojson.jq $(TMP_DIR) $(FAIR_JSON)
	rm -f $@
	jq --indent N -f $< $(FAIR_JSON_GLOB) >> $@

$(TMP_DIR)/exhibitor.geo.json : $(TMP_DIR)/exhibitor.jsonl
	rm -f $@
	jq -s '{"type": "FeatureCollection", "features": .}' $^ >> $@

image/exhibitor.png : $(TMP_DIR)/exhibitor.geo.json $(MAP_ASSETS) tools/heatmap.js
	$(VENV)/bin/python tools/map.py -v -j heatmap.js $< $@


$(TMP_DIR)/iso2.%.exhibitor-travel.json : $(FAIR_JSON) tools/travel.jq $(TMP_DIR)
	rm -f $@
	jq -s --arg iso2 $* -f tools/exhibitor-travel.jq $(FAIR_JSON_GLOB) >> $@

image/iso2.%.exhibitor-travel.png : $(TMP_DIR)/iso2.%.exhibitor-travel.json $(MAP_ASSETS) tools/exhibitor-travel.js
	$(VENV)/bin/python tools/map.py -v -j exhibitor-travel.js $< $@


$(TMP_DIR)/%.exhibitor-travel.json : data/%.json tools/exhibitor-travel.jq $(TMP_DIR)
	rm -f $@
	jq -s -f tools/exhibitor-travel.jq $< >> $@

$(IMAGE_FAIR_DIR)/%.exhibitor-travel.png : $(TMP_DIR)/%.exhibitor-travel.json $(IMAGE_FAIR_DIR) $(MAP_ASSETS) tools/exhibitor-travel.js
	$(VENV)/bin/python tools/map.py -v -j exhibitor-travel.js $< $@

$(TMP_DIR)/%.exhibitor-country.json : data/%.json tools/exhibitor-country.jq $(TMP_DIR)
	rm -f $@
	jq -s -f tools/exhibitor-country.jq --rawfile countryGeoCsv tools/country.geo.csv $< > $@

$(IMAGE_FAIR_DIR)/%.exhibitor-country.png : $(TMP_DIR)/%.exhibitor-country.json $(IMAGE_FAIR_DIR) $(MAP_ASSETS) tools/exhibitor-country.js
	$(VENV)/bin/python tools/map.py -v -j exhibitor-country.js $< $@

$(IMAGE_FAIR_DIR)/%.exhibitor-address-gb.png : $(TMP_DIR)/%.exhibitor-travel.json $(IMAGE_FAIR_DIR) $(MAP_ASSETS) tools/exhibitor-address-gb.js
	$(VENV)/bin/python tools/map.py -v -j exhibitor-address-gb.js $< $@


$(TMP_DIR)/category.txt : tools/category.jq $(FAIR_JSON) 
	rm -f $@
	jq -sr -f $< $(FAIR_JSON_GLOB) >> $@

image/category.png : $(TMP_DIR) $(TMP_DIR)/category.txt
# Add `--no_collocations` to disable bigrams
	$(VENV)/bin/wordcloud_cli --text $^ \
	  --width=1200 --height=600 --margin=15 \
	  --background="#FAFAFA" --color="#E20613" \
	  --imagefile $@


tools/country.geo.json : $(FAIR_JSON) tools/country.geo.jq
	rm -f $@
	jq -s -f tools/country.geo.jq $(FAIR_JSON_GLOB) >> $@


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

