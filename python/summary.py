#!/usr/bin/env python3

import csv
import json
import logging
import argparse
from pathlib import Path

import jsonschema



LOG = logging.getLogger("summary")



def main():
    parser = argparse.ArgumentParser(
        description="Read fair JSON files and produce a summary in CSV format.")

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
        nargs="+",
        help="Path to JSON input files.")

    parser.add_argument(
        "csv_path",
        metavar="CSV",
        type=Path,
        help="Path to CSV output file.")

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

    titles = (
        "Slug",
        "Start date",
        "End date",
        "Organiser",
        "Exhibitor",
        "Delegation",
        "Website",
    )

    out = [titles]
    last_series = None
    for path in args.json_path:
        data = json.loads(path.read_text())

        organiser = data.get("organiser", "")
        if organiser:
            organiser = 1 if isinstance(organiser, dict) else len(organiser)
        exhibitor = data.get("exhibitor", "")
        if exhibitor:
            exhibitor = 1 if isinstance(exhibitor, dict) else len(exhibitor)
        delegation = data.get("delegation", "")
        if delegation:
            delegation = 1 if isinstance(delegation, dict) else len(delegation)
        website = data.get("website", "")
        if website and not isinstance(website, str):
            website = " ".join(website)

        series = data.get("series", None)
        if series != last_series:
            out.append(["", ] * len(titles))
            last_series = series

        out.append((
            path.stem,
            data.get("startDate", ""),
            data.get("endDate", ""),
            str(organiser),
            str(exhibitor),
            str(delegation),
            website,
        ))

    writer = csv.writer(args.csv_path.open("w"))
    writer.writerows(out)




if __name__ == "__main__":
    main()
