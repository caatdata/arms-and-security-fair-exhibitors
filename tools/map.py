#!/usr/bin/env python3

import re
import json
import time
import base64
import argparse
import logging
import threading
import http.server
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

LOG = logging.getLogger("map")
TOOLS_PATH = Path(__file__).parent
REPO_PATH = TOOLS_PATH.parent
PRIVATE = json.loads((REPO_PATH / ".private.json").read_text("utf-8"))



def request_handler_factory(path_dict, replace_dict):
    class RequestHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            path = Path(self.path[1:])
            if "/" in str(path):
                self.send_response(404)
                self.end_headers()
                return

            path = path_dict.get(path.name, TOOLS_PATH / path)

            try:
                content_type = {
                    ".ico": "image/x-icon",
                    ".png": "image/png",

                    ".html": "text/html",
                    ".css": "text/css",
                    ".js": "text/javascript",

                    ".json": "application/json",
                }[path.suffix]
            except KeyError:
                self.send_response(404)
                self.end_headers()
                return

            try:
                body = path.read_bytes()
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
                return

            if not content_type.startswith("image/"):
                body = body.decode("utf-8")
                for pattern, lookup in replace_dict.items():
                    if re.search(pattern, path.name):
                        for key, value in lookup.items():
                            body = body.replace(key, value)
                body = body.encode("utf-8")

            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.end_headers()
            self.wfile.write(body)


    return RequestHandler



def map_to_png(path_dict, replace_dict, png_path, driver_path):
    handler_class = request_handler_factory(path_dict, replace_dict)

    server = http.server.ThreadingHTTPServer(("", 8000), handler_class)
    LOG.info("Starting Server in background.")
    thread = threading.Thread(target = server.serve_forever)
    thread.daemon = True
    thread.start()

    time.sleep(1)

    chrome_options = Options()
    chrome_options.set_capability('goog:loggingPrefs', {
        "browser": "ALL",
    })
    service = Service(driver_path)

    LOG.info("Starting Chromedriver.")
    driver = webdriver.Chrome(
        options=chrome_options,
        service=service,
    )
    driver.get("http://0.0.0.0:8000/map.html")
    for item in driver.get_log('browser'):
        LOG.warning(f"{item['level']}: {item['message']}")
    time.sleep(2)

    LOG.info("Requesting canvas data.")
    result = driver.execute_script("return mapPng();")
    head = "data:image/png;base64,"
    assert result.startswith(head)
    png_data = base64.b64decode(result[len(head):])

    LOG.info(f"Writing canvas data to `{png_path}`.")
    with png_path.open("wb") as fp:
        fp.write(png_data)

    LOG.info("Closing Chromedriver.")
    driver.close()

    LOG.info("Stopping Server.")
    server.shutdown()

    thread.join()
    LOG.info("Done.")



def main():
    parser = argparse.ArgumentParser(
        description="Produce a map PNG from JSON location data.")

    parser.add_argument(
        "--verbose", "-v",
        action="count",
        help="Print verbose information for debugging.", default=0)
    parser.add_argument(
        "--quiet", "-q",
        action="count",
        help="Suppress warnings.", default=0)

    parser.add_argument(
        "--javascript", "-j",
        type=Path,
        action="append",
        help="Path to Javascript file to load.")

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
    for log in (LOG, ):
        log.addHandler(logging.StreamHandler())
        log.setLevel(level)

    path_dict = {
        args.json_path.name: args.json_path
    }

    replace_dict = {
        r"^map\.html$": {
            "__SCRIPT__": "\n".join([
                f'    <script src="{v}"></script>'
                for v in (["map.js"] + args.javascript)
            ])
        },
        r"^.*\.js$": {
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
