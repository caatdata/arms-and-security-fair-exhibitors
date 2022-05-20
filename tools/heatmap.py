#!/usr/bin/env python3

import json
import base64
import time
import logging
import argparse
import threading
import http.server
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

LOG = logging.getLogger("task")
TOOLS_PATH = Path(__file__).parent
REPO_PATH = TOOLS_PATH.parent
PRIVATE = json.loads((REPO_PATH / ".private.json").read_text("utf-8"))
GEO_JSON_NAME = None



class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        path = Path(self.path[1:])
        if "/" in str(path):
            self.send_response(404)
            self.end_headers()
            return

        path = TOOLS_PATH / path

        try:
            content_type = {
                ".ico": "image/x-icon",
                ".html": "text/html",
                ".js": "text/javascript",
                ".css": "text/css",
                ".json": "application/json"
            }[path.suffix]
        except KeyError:
            self.send_response(404)
            self.end_headers()
            return

        try:
            body = path.read_text("utf-8")
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            return

        if path.name == "heatmap.js":
            body = body.replace("__MAPBOX_API_KEY__", json.dumps(PRIVATE["mapboxApiKey"]))
            body = body.replace("__GEO_JSON_NAME__", json.dumps(GEO_JSON_NAME))

        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))



def main():
    global GEO_JSON_NAME

    parser = argparse.ArgumentParser(
        description="Determine scraping tasks based on event dates.")

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
    LOG.addHandler(logging.StreamHandler())
    LOG.setLevel(level)


    print(args.json_path)
    GEO_JSON_NAME = args.json_path.name
    print(args.json_path.name)


    server = http.server.ThreadingHTTPServer(("", 8000), RequestHandler)
    LOG.info("Starting Server in background.")
    thread = threading.Thread(target = server.serve_forever)
    thread.daemon = True
    thread.start()

    time.sleep(1)

    chrome_options = Options()
    chrome_options.set_capability('goog:loggingPrefs', {
        "browser": "ALL",
    })
    service = Service(PRIVATE["chromedriverPath"])

    LOG.info("Starting Chromedriver.")
    driver = webdriver.Chrome(
        options=chrome_options,
        service=service,
    )
    driver.get("http://0.0.0.0:8000/heatmap.html")
    for item in driver.get_log('browser'):
        LOG.warning(f"{item['level']}: {item['message']}")
    time.sleep(2)

    LOG.info("Requesting canvas data.")
    result = driver.execute_script("return mapPng();")
    head = "data:image/png;base64,"
    assert result.startswith(head)
    png_data = base64.b64decode(result[len(head):])

    LOG.info(f"Writing canvas data to `{args.png_path}`.")
    with args.png_path.open("wb") as fp:
        fp.write(png_data)

    LOG.info("Closing Chromedriver.")
    driver.close()

    LOG.info("Stopping Server.")
    server.shutdown()

    thread.join()
    LOG.info("Done.")



if __name__ == "__main__":
    main()
