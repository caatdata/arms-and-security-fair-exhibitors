#!/usr/bin/env python3

import io
import csv
import sys
import json
import shutil
import logging
import argparse
from pathlib import Path

import jsonschema

sys.path.append(Path(__file__).parent)

from common import Fair



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
        "Alias",
    )

    count = {
        "series": 0,
        "events": 0,
        "exhibitors": 0,
        "organisers": 0,
        "delegations": 0,
    }

    out = [titles]
    last_series = None
    for path in args.json_path:
        fair = Fair(path)
        count["organisers"] += len(fair.organiser)
        count["exhibitors"] += len(fair.exhibitor)
        count["delegations"] += len(fair.delegation)
        website = " ".join(fair.website)
        alias = ";".join(fair.alias)

        series = fair.series
        if series != last_series:
            out.append(["", ] * len(titles))
            last_series = series
            count["series"] += 1

        out.append((
            fair.slug,
            fair.start_date or "",
            fair.end_date or "",
            str(len(fair.organiser) or ""),
            str(len(fair.exhibitor) or ""),
            str(len(fair.delegation) or ""),
            website,
            alias,
        ))
        count["events"] += 1

    writer = csv.writer(args.csv_path.open("w"))
    writer.writerows(out)

    readme_path = Path("README.md")
    readme = readme_path.read_text("utf-8")
    readme_out = io.StringIO()
    section = 0
    for line in readme.splitlines():
        if "## Statistics" in line:
            section = 1
            readme_out.write(line + "\n")
            readme_out.write("\n")
            for k, v in count.items():
                readme_out.write(f"-   **{v}** {k}\n")
            readme_out.write("\n")
            readme_out.write("\n")
        elif "##" in line:
            section = 2

        if section in (0, 2):
            readme_out.write(line + "\n")


    with readme_path.open("w") as fp:
        readme_out.seek(0)
        shutil.copyfileobj(readme_out, fp)




if __name__ == "__main__":
    main()
