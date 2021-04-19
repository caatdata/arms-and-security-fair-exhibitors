#!/usr/bin/env python3

import json
from pathlib import Path

import jsonschema

fair_schema = json.loads(Path("schema/fair.schema.json").read_text(encoding="utf-8"))

for path in Path("data").glob("*"):
    jsonschema.validate(json.loads(path.read_text(encoding="utf-8")), fair_schema)
