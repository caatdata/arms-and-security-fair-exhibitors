import time
import base64
import logging
import threading
import http.server
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

TOOLS_PATH = Path(__file__).parent

LOG = logging.getLogger("map")



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

            for key, value in replace_dict.get(path.name, {}).items():
                body = body.replace(key, value)

            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.end_headers()
            self.wfile.write(body.encode("utf-8"))


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
