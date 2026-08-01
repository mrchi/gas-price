# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "requests>=2.33.0",
# ]
# ///
import json
import os
import pathlib
from datetime import date, datetime, timedelta

import requests

DATA_DIR = pathlib.Path(__file__).parent.parent / "data"
GAS_PRICE_FILE = DATA_DIR / "china_gas.json"
CRUDE_OIL_PRICE_FILE = DATA_DIR / "crude_oil.json"
OILPRICEAPI_APIKEY = os.getenv("OILPRICEAPI_APIKEY")


def main():
    china_gas_data = json.loads(GAS_PRICE_FILE.read_text(encoding="utf-8"))
    crude_oil_data = json.loads(CRUDE_OIL_PRICE_FILE.read_text(encoding="utf-8"))
    dates_should_update = {
        i["update_time"] for i in china_gas_data["price_history"]
    } - {i["update_time"] for i in crude_oil_data["price_history"]}

    if not dates_should_update:
        print("No update needed.")
        return

    if len(dates_should_update) != 1:
        raise RuntimeError("Historical data needs to be updated manually.")

    target_date = dates_should_update.pop()
    if not OILPRICEAPI_APIKEY:
        raise RuntimeError("OILPRICEAPI_APIKEY is not configured.")

    resp = requests.get(
        url="https://api.oilpriceapi.com/v1/prices/latest",
        params={"by_code": "BRENT_CRUDE_USD"},
        headers={"Authorization": f"Token {OILPRICEAPI_APIKEY}"},
        timeout=10,
    )
    resp.raise_for_status()
    oil_data = resp.json()["data"]

    if oil_data.get("code") != "BRENT_CRUDE_USD":
        raise ValueError(f"Unexpected crude oil code: {oil_data.get('code')}")
    if oil_data.get("type") != "spot_price":
        raise ValueError(f"Unexpected crude oil price type: {oil_data.get('type')}")

    source_date = datetime.fromisoformat(oil_data["created_at"]).date()
    adjustment_date = date.fromisoformat(target_date.split()[0])
    if abs(source_date - adjustment_date) > timedelta(days=3):
        raise ValueError(
            f"Latest Brent price is too far from the adjustment date: "
            f"source={source_date}, adjustment={adjustment_date}"
        )

    crude_oil_data["price_history"].insert(
        0,
        {"update_time": target_date, "price": oil_data["price"]},
    )
    with open(CRUDE_OIL_PRICE_FILE, "w", encoding="utf-8") as f:
        json.dump(crude_oil_data, f, ensure_ascii=False, indent=2)
    print("Data updated successfully.")


if __name__ == "__main__":
    main()
