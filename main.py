import logging
import os
import sys

import requests
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class MissingEnvironmentVariable(Exception):
    pass


def load_variable(var_name):
    var = os.getenv(var_name)
    if not var:
        raise MissingEnvironmentVariable(f"Environment variable {var_name} not set")
    return var


HETZNER_BASE_URL = "https://api.hetzner.cloud"
ZONE_NAME = load_variable("ZONE_NAME")
RECORD_NAME = load_variable("RECORD_NAME")
API_TOKEN = load_variable("API_TOKEN")

AUTH_HEADER = {"Authorization": f"Bearer {API_TOKEN}"}

zones_response = requests.get(f"{HETZNER_BASE_URL}/v1/zones", headers=AUTH_HEADER)
zones_response.raise_for_status()
zone_id = next(
    (
        zone["id"]
        for zone in zones_response.json()["zones"]
        if zone["name"] == ZONE_NAME
    ),
    None,
)
if zone_id is None:
    logger.info("Zone not found")
    sys.exit(1)

logger.info("Zone id: %s", zone_id)

current_ip = requests.get("https://v4.ident.me").text
logger.info("Current IP: %s", current_ip)

rrsets_response = requests.get(
    f"{HETZNER_BASE_URL}/v1/zones/{zone_id}/rrsets",
    headers=AUTH_HEADER,
)
rrsets_response.raise_for_status()
rrset = next(
    (
        record
        for record in rrsets_response.json()["rrsets"]
        if record["name"] == RECORD_NAME and record["type"] == "A"
    ),
    None,
)

if not rrset:
    logger.info("Create record")
    create_response = requests.post(
        f"{HETZNER_BASE_URL}/v1/zones/{zone_id}/rrsets",
        json={
            "name": RECORD_NAME,
            "type": "A",
            "ttl": 60,
            "records": [{"value": current_ip, "comment": ""}],
        },
        headers=AUTH_HEADER,
    ).json()
    logger.info("Record created: %s", create_response)
else:
    records = rrset.get("records", [])
    if records and records[0]["value"] != current_ip:
        logger.info("Update record")
        update_response = requests.post(
            f"{HETZNER_BASE_URL}/v1/zones/{zone_id}/rrsets/{RECORD_NAME}/A/actions/set_records",
            json={
                "records": [{"value": current_ip, "comment": ""}],
            },
            headers=AUTH_HEADER,
        ).json()
        logger.info("Record updated: %s", update_response)
    else:
        logger.info("IP is up to date. Nothing to do")
