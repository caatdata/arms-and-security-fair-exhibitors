#!/usr/bin/env python3

import sys
import json
import logging
import argparse
from pathlib import Path

LOG = logging.getLogger("travel_map")
TOOLS_PATH = Path(__file__).parent
REPO_PATH = TOOLS_PATH.parent
PRIVATE = json.loads((REPO_PATH / ".private.json").read_text("utf-8"))

sys.path.append(TOOLS_PATH)

from map import map_to_png



def main():
    parser = argparse.ArgumentParser(
        description="Produce a travel map PNG from JSON location data.")

    parser.add_argument(
        "--verbose", "-v",
        action="count",
        help="Print verbose information for debugging.", default=0)
    parser.add_argument(
        "--quiet", "-q",
        action="count",
        help="Suppress warnings.", default=0)

    parser.add_argument(
        "json_path",
        metavar="JSON",
        type=Path,
        help="Path to input GeoJSON.")

    parser.add_argument(
        "png_path",
        metavar="PNG",
        type=Path,
        help="Path to output PNG.")


    args = parser.parse_args()

    offset = args.verbose - args.quiet if args else 0
    level = (
        logging.FATAL,
        logging.ERROR,
        logging.WARNING,
        logging.INFO,
        logging.DEBUG
    )[max(0, min(4, 2 + offset))]
    for log in (LOG, logging.getLogger("map")):
        log.addHandler(logging.StreamHandler())
        log.setLevel(level)

    path_dict = {
        args.json_path.name: args.json_path
    }

    replace_dict = {
        "map.html": {
            "__SCRIPT__": "travel-map.js",
        },
        "travel-map.js": {
            "__MAPBOX_API_KEY__": json.dumps(PRIVATE["mapboxApiKey"]),
            "__GEO_JSON_NAME__": json.dumps(args.json_path.name),
        },
    }

    map_to_png(
        path_dict, replace_dict,
        args.png_path,
        driver_path=PRIVATE["chromedriverPath"]
    )



if __name__ == "__main__":
    main()
