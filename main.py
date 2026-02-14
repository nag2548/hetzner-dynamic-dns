import os

import requests
from dotenv import load_dotenv

load_dotenv()


class MissingEnvironmentVariable(Exception):
    pass


def load_environment_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        raise MissingEnvironmentVariable(f"Environment variable {var_name} not set")


HETZNER_BASE_URL = "https://api.hetzner.cloud"
ZONE_NAME = load_environment_variable("ZONE_NAME")
RECORD_NAME = load_environment_variable("RECORD_NAME")
API_TOKEN = load_environment_variable("API_TOKEN")

AUTH_HEADER = {"Authorization": f"Bearer {API_TOKEN}"}

zones_response = requests.get(
    f"{HETZNER_BASE_URL}/v1/zones", headers=AUTH_HEADER
).json()
zone_id = next(
    (zone["id"] for zone in zones_response["zones"] if zone["name"] == ZONE_NAME), None
)
if zone_id is None:
    print("Zone not found")
    exit(1)

print("Zone id: ", zone_id)

current_ip = requests.get("https://v4.ident.me").text
print("Current IP: ", current_ip)

record_response = requests.get(
    f"{HETZNER_BASE_URL}/v1/zones/{zone_id}/rrsets/{RECORD_NAME}/A",
    headers=AUTH_HEADER,
)
if record_response.status_code == 404:
    print("Create record")
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
    print("Record created: ", create_response)
elif record_response.status_code == 200:
    record = record_response.json()
    if (
        record["rrset"]["records"]
        and record["rrset"]["records"][0]["value"] != current_ip
    ):
        print("Update record")
        update_response = requests.post(
            f"{HETZNER_BASE_URL}/v1/zones/{zone_id}/rrsets/{RECORD_NAME}/A/actions/set_records",
            json={
                "records": [{"value": current_ip, "comment": ""}],
            },
            headers=AUTH_HEADER,
        ).json()
        print("Record updated: ", update_response)
    else:
        print("IP is up to date. Nothing to do")
