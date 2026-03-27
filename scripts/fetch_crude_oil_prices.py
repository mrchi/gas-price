# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "requests>=2.33.0",
# ]
# ///
import json
import os
import pathlib
from datetime import datetime

import requests

DATA_DIR = pathlib.Path(__file__).parent.parent / "data"
GAS_PRICE_FILE = DATA_DIR / "china_gas.json"
CRUDE_OIL_PRICE_FILE = DATA_DIR / "crude_oil.json"
OILPRICEAPI_APIKEY = os.getenv("OILPRICEAPI_APIKEY")


def main():
    china_gas_data = json.loads(GAS_PRICE_FILE.read_text(encoding="utf-8"))
    crude_oil_data = json.loads(CRUDE_OIL_PRICE_FILE.read_text(encoding="utf-8"))
    dates_should_update = set(
        i["update_time"] for i in china_gas_data["price_history"]
    ) - set(i["update_time"] for i in crude_oil_data["price_history"])

    if not dates_should_update:
        print("No update needed.")
        return

    resp = requests.get(
        url="https://api.oilpriceapi.com/v1/prices/past_week",
        params={"by_code": "BRENT_CRUDE_USD", "interval": "1d"},
        headers={"Authorization": f"Token {OILPRICEAPI_APIKEY}"},
    )
    resp.raise_for_status()
    prices = resp.json()["data"]["prices"]

    update_flag = False
    for price in prices:
        date = datetime.fromisoformat(price["created_at"]).strftime("%Y-%m-%d 00:00:00")
        if date not in dates_should_update:
            continue
        data = {
            "update_time": date,
            "price": price["price"],
        }
        crude_oil_data["price_history"].insert(0, data)
        update_flag = True

    if update_flag:
        with open(CRUDE_OIL_PRICE_FILE, "w", encoding="utf-8") as f:
            json.dump(crude_oil_data, f, ensure_ascii=False, indent=2)
        print("Data updated successfully.")
    else:
        print("No new data to update.")


if __name__ == "__main__":
    main()
