#!/usr/bin/env python3

import re
import sys
import json
import logging
import argparse
import datetime
from statistics import mean
from pathlib import Path
from collections import defaultdict


LOG = logging.getLogger("task")


BEFORE_INTERVAL = datetime.timedelta(days=180)
IGNORE_INTERVAL = datetime.timedelta(days=365)
UPDATE_INTERVAL = datetime.timedelta(days=30)



def split(slug):
    return slug[:-5], slug[-4:]



def main():
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
        "ignore_path",
        metavar="IGNORE",
        type=Path,
        help="Path to event ignore JSON file.")

    parser.add_argument(
        "data_path",
        metavar="DATA",
        type=Path,
        help="Path to event data directory.")

    parser.add_argument(
        "--new", "-n",
        action="store_true",
        help="List potential new events.")
    parser.add_argument(
        "--exhibitor", "-e",
        action="store_true",
        help="List current events that are lacking exhibitor lists.")
    parser.add_argument(
        "--outdated", "-o",
        action="store_true",
        help="List events whose exhibitor lists might be outdated.")

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

    today = datetime.datetime.now().date()
    fair_dict = defaultdict(dict)

    for path in args.data_path.glob("*.json"):
        slug = path.stem
        data = json.loads(path.read_text())

        if not re.match(r"\d{4}$", data["edition"]):
            LOG.warning("%s: Ignoring non-year edition %s.", path, repr(data["edition"]))
            continue

        series_slug, year = split(slug)
        assert not year in fair_dict[series_slug]
        item = {
            "endDate": data["endDate"],
            "website": data.get("website", None),
            "exhibitor": bool(data.get("exhibitor", None)),
            "exhibitorListDate": data.get("exhibitorListDate", None),
            "exhibitorListUrl": data.get("exhibitorListUrl", None),
        }
        item["endDate"] = datetime.datetime.strptime(
            item["endDate"], "%Y-%m-%d").date()
        if item["exhibitorListDate"]:
            item["exhibitorListDate"] = datetime.datetime.strptime(
                item["exhibitorListDate"][:10], "%Y-%m-%d").date()
        fair_dict[series_slug][year] = item


    for line in args.ignore_path.read_text().split("\n")[1: ]:
        if not line.strip():
            continue
        slug = line.split(",", 1)[0].strip()
        series_slug, year = split(slug)
        assert not year in fair_dict[series_slug]
        fair_dict[series_slug][year] = False

    category = {
        "new": "Check for new fairs",
        "exhibitor": "Check for exhibitor lists",
        "update": "Update exhibitor lists",
    }
    tasks = {v: [] for v in category}


    for series_slug in sorted(list(fair_dict.keys())):
        LOG.debug(series_slug)
        last_year = None
        last_data = None
        years = sorted(list(fair_dict[series_slug]))
        for y, year in enumerate(years):
            data = fair_dict[series_slug][year]
            LOG.debug(" " + year + " " + str(data and data["endDate"]))
            year = int(year)

            if (last_year or len(years) == 1) and (data or last_data):
                next_year = year * 2 - last_year if last_year else year + 1
                LOG.debug("  " + repr((last_year, year, next_year)))
                # Average day of year
                doy = mean([
                    float(int(v["endDate"].strftime("%j")))
                    for v in (last_data, data) if v
                ])
                website = " ".join(set([
                    repr(v["website"])
                    for v in (last_data, data) if v and v.get("website", None)
                ] + [
                    repr(v["exhibitorListUrl"])
                    for v in (last_data, data) if v and v.get("exhibitorListUrl", None)
                ]))

                if str(next_year) not in fair_dict[series_slug]:
                    end_date = (
                            datetime.datetime(next_year, 1, 1) +
                            datetime.timedelta(days=doy - 1)
                        ).date()
                    if (
                            end_date > today - IGNORE_INTERVAL and
                            end_date < today + BEFORE_INTERVAL
                    ):
                        slug = f"{series_slug}-{next_year}"
                        tasks["new"].append({
                            "slug": slug,
                            "endDate": end_date,
                            "website": website,
                        })

            last_year = year
            last_data = data

        if data:
            slug = f"{series_slug}-{year}"
            if data["endDate"] > today - IGNORE_INTERVAL:
                if not data["exhibitor"] and data["endDate"] < today + BEFORE_INTERVAL:
                    tasks["exhibitor"].append({
                        "slug": slug,
                        "endDate": data["endDate"],
                        "website": data.get("website", None),
                    })
                elif (
                        data["exhibitorListDate"] and
                        data["exhibitorListDate"] < data["endDate"] and
                        data["exhibitorListDate"] < today - UPDATE_INTERVAL
                ):
                    tasks["update"].append({
                        "slug": slug,
                        "endDate": data["endDate"],
                        "website": data.get("website", None),
                        "exhibitorListDate": data["exhibitorListDate"],
                    })


    for k, message in category.items():
        if tasks[k]:
            print(f"{message}:")
            for item in sorted(tasks[k], key=lambda x: x["endDate"]):
                print(f"  {item['slug']}")
                print(f"    Date:    {item['endDate']}")
                print(f"    Website: {item['website']}")
                if "exhibitorListDate" in item:
                    print(f"    Scraped: {item['exhibitorListDate']}")

                print()
            print()








if __name__ == "__main__":
    main()
