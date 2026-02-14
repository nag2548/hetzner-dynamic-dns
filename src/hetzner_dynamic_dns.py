import logging
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MissingEnvironmentVariable(Exception):
    pass


def load_variable(var_name):
    var = os.getenv(var_name)
    if not var:
        raise MissingEnvironmentVariable(f"Environment variable {var_name} not set")
    return var


def main():
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=env_path, override=False)

    hetzner_base_url = "https://api.hetzner.cloud"
    zone_name = load_variable("ZONE_NAME")
    record_name = load_variable("RECORD_NAME")
    api_token = load_variable("API_TOKEN")

    auth_header = {"Authorization": f"Bearer {api_token}"}
    timeout = 15

    zones_response = requests.get(
        f"{hetzner_base_url}/v1/zones", headers=auth_header, timeout=timeout
    )
    zones_response.raise_for_status()

    zone_id = next(
        (
            zone["id"]
            for zone in zones_response.json()["zones"]
            if zone["name"] == zone_name
        ),
        None,
    )
    if zone_id is None:
        logger.info("Zone not found")
        return 1

    logger.info("Zone id: %s", zone_id)

    current_ip = requests.get("https://v4.ident.me", timeout=timeout).text.strip()
    logger.info("Current IP: %s", current_ip)

    rrsets_response = requests.get(
        f"{hetzner_base_url}/v1/zones/{zone_id}/rrsets",
        headers=auth_header,
        timeout=timeout,
    )
    rrsets_response.raise_for_status()

    rrset = next(
        (
            record
            for record in rrsets_response.json()["rrsets"]
            if record["name"] == record_name and record["type"] == "A"
        ),
        None,
    )

    if not rrset:
        logger.info("Create record")
        create_response = requests.post(
            f"{hetzner_base_url}/v1/zones/{zone_id}/rrsets",
            json={
                "name": record_name,
                "type": "A",
                "ttl": 60,
                "records": [{"value": current_ip, "comment": ""}],
            },
            headers=auth_header,
            timeout=timeout,
        ).json()
        logger.info("Record created: %s", create_response)
        return 0

    records = rrset.get("records", [])
    if records and records[0]["value"] != current_ip:
        logger.info("Update record")
        update_response = requests.post(
            f"{hetzner_base_url}/v1/zones/{zone_id}/rrsets/{record_name}/A/actions/set_records",
            json={
                "records": [{"value": current_ip, "comment": ""}],
            },
            headers=auth_header,
            timeout=timeout,
        ).json()
        logger.info("Record updated: %s", update_response)
        return 0

    logger.info("IP is up to date. Nothing to do")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except MissingEnvironmentVariable as e:
        logger.error(str(e))
        raise SystemExit(2)
    except requests.RequestException as e:
        logger.exception("Network/API error: %s", e)
        raise SystemExit(3)
