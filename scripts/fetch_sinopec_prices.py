# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "requests>=2.33.0",
# ]
# ///
import json
import pathlib

import requests

SWITCH_PROVINCE_URL = "https://cx.sinopecsales.com/yjkqiantai/data/switchProvince"
INIT_OIL_PRICE_URL = "https://cx.sinopecsales.com/yjkqiantai/data/initOilPrice"
PROVINCE_ID = "11"  # Beijing
CURRENT_DATA_PATH = pathlib.Path(__file__).parent.parent / "data" / "china_gas.json"
HEADERS = {
    "Content-Type": "application/json;charset=UTF-8",
    "Origin": "https://cx.sinopecsales.com",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1",
}


def main():
    # Initialize session
    session = requests.Session()
    session.headers.update(HEADERS)

    print("Step 1/3: Calling switchProvince API...")
    session.headers["Referer"] = "https://cx.sinopecsales.com/yjkqiantai/core/main"
    resp = session.post(
        SWITCH_PROVINCE_URL, json={"provinceId": PROVINCE_ID}, timeout=10
    )
    resp.raise_for_status()

    print("Step 2/3: Calling initOilPrice API...")
    session.headers["Referer"] = (
        "https://cx.sinopecsales.com/yjkqiantai/core/toHistoryOilPrice"
    )
    resp = session.get(INIT_OIL_PRICE_URL, timeout=10)
    resp.raise_for_status()
    province_data = resp.json()["data"]["provinceData"]

    # Load existing data for comparison
    print("Step 3/3: Loading existing data for comparison...")
    with open(CURRENT_DATA_PATH, "r", encoding="utf-8") as f:
        existing_data = json.load(f)
    latest_existing_date = max(i["update_time"] for i in existing_data["price_history"])

    # Map API entries to our price_history format
    update_flag = False
    for entry in province_data:
        if entry["START_TIME"] <= latest_existing_date:
            continue
        price_entry = {
            "update_time": entry["START_TIME"],
            "gas_92": {
                "price": float(entry["GAS_92"]),
                "change": float(entry.get("GAS_92_STATUS", 0.0)),
            },
            "gas_95": {
                "price": float(entry["GAS_95"]),
                "change": float(entry.get("GAS_95_STATUS", 0.0)),
            },
            "gas_98": {
                "price": float(entry["AIPAO_GAS_98"]),
                "change": float(entry.get("AIPAO_GAS_98_STATUS", 0.0)),
            },
        }
        existing_data["price_history"].insert(0, price_entry)
        update_flag = True

    if update_flag:
        with open(CURRENT_DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        print("Data updated successfully.")
    else:
        print("No new data to update.")


if __name__ == "__main__":
    main()
