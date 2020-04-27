#!/usr/bin/env python3

from datetime import datetime, timedelta, timezone
from tzlocal import get_localzone
import os
import dateutil.parser as dateparser
from decimal import Decimal
from io import StringIO

import requests

import singer
from singer import utils
import csv
from ast import literal_eval

LOGGER = singer.get_logger()
SESSION = requests.Session()
REQUIRED_CONFIG_KEYS = [
    "sa_hostnames",
    "sa_user_id",
    "sa_api_key",
    "sa_start_date",
]

CONFIG = {}
STATE = {}
BASE_URL = "https://simpleanalytics.com/api/export/{}?hostname={}&start={}&end={}&timezone=UTC"

def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)

def load_schema(entity):
    return utils.load_json(get_abs_path("schemas/{}.json".format(entity)))

def get_start(key, useStartDate=True):
    if key not in STATE:
        if useStartDate:
            d = utils.strptime_with_tz(CONFIG['sa_start_date'])
            STATE[key] = utils.strftime(d)
            return d
        else:
            return None
    else:
        return dateparser.parse(STATE[key])

def get_urls(endpoint, start, end):
    return map(lambda hostname: get_url(endpoint, hostname, start, end), CONFIG['sa_hostnames'])


def get_url(endpoint, hostname, start, end):
    return BASE_URL.format(endpoint, hostname, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))

INT_FIELDS=["added_unix", "scrolled_percentage", "duration_seconds", "device_width_pixels", "device_width"]

def sync_type(type, endpoint, replicationKey):
    schema = load_schema(type)
    singer.write_schema(type, schema, [replicationKey])

    urls = get_urls(endpoint, get_start(type), datetime.now())

    lastRow = None

    for url in urls:
        singer.log_info(url)

        headers = {
            "Content-Type": "text/csv",
            "User-Id": CONFIG["sa_user_id"],
            "Api-Key": CONFIG["sa_api_key"]
        }

        req = requests.Request("GET", url=url, headers=headers).prepare()
        resp = SESSION.send(req)
        resp.raise_for_status()

        reader = csv.DictReader(resp.text.split('\n'), delimiter=',')

        for row in reader:
            # print(row)
            if row.get("added_iso"):
                row["added_iso"] = utils.strftime(dateparser.parse(row["added_iso"]))
            if row.get("is_unique"):
                row["is_unique"] = row["is_unique"] == "true"
            for k in INT_FIELDS:
                if row.get(k) or row.get(k) == "" :
                    row[k] = None if row[k] == "" else literal_eval(row[k])
            singer.write_record(type, row)
            if lastRow == None or row["added_iso"] > lastRow["added_iso"]:
                lastRow = row

    if lastRow != None:
        utils.update_state(STATE, type, dateparser.parse(lastRow['added_iso']).strftime("%Y-%m-%d"))

def do_sync():
    LOGGER.info("Starting sync")

    sync_type("visits", "visits", "added_iso")
    # sync_type("events", "events", "added_iso")

    singer.write_state(STATE)

    LOGGER.info("Sync complete")

def main():
    args = utils.parse_args(REQUIRED_CONFIG_KEYS)
    CONFIG.update(args.config)
    STATE.update(args.state)
    do_sync()

if __name__ == "__main__":
    main()
