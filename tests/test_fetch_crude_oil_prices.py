import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import fetch_crude_oil_prices


class FakeResponse:
    def raise_for_status(self):
        pass

    def json(self):
        return {
            "data": {
                "code": "BRENT_CRUDE_USD",
                "type": "spot_price",
                "created_at": "2026-08-01T04:31:31.333Z",
                "price": 91.04,
            }
        }


class FetchCrudeOilPricesTest(unittest.TestCase):
    def test_uses_gas_adjustment_date_for_latest_spot_price(self):
        with tempfile.TemporaryDirectory() as directory:
            data_dir = Path(directory)
            gas_file = data_dir / "china_gas.json"
            crude_file = data_dir / "crude_oil.json"
            gas_file.write_text(
                json.dumps(
                    {
                        "price_history": [
                            {"update_time": "2026-08-01 00:00:00"},
                            {"update_time": "2026-07-18 00:00:00"},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            crude_file.write_text(
                json.dumps(
                    {
                        "price_history": [
                            {
                                "update_time": "2026-07-18 00:00:00",
                                "price": 85.92,
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            with (
                patch.object(fetch_crude_oil_prices, "GAS_PRICE_FILE", gas_file),
                patch.object(
                    fetch_crude_oil_prices, "CRUDE_OIL_PRICE_FILE", crude_file
                ),
                patch.object(
                    fetch_crude_oil_prices,
                    "OILPRICEAPI_APIKEY",
                    "test-token",
                ),
                patch.object(
                    fetch_crude_oil_prices.requests,
                    "get",
                    return_value=FakeResponse(),
                ) as request,
            ):
                fetch_crude_oil_prices.main()

            request.assert_called_once_with(
                url="https://api.oilpriceapi.com/v1/prices/latest",
                params={"by_code": "BRENT_CRUDE_USD"},
                headers={"Authorization": "Token test-token"},
                timeout=10,
            )
            result = json.loads(crude_file.read_text(encoding="utf-8"))
            self.assertEqual(
                result["price_history"][0],
                {"update_time": "2026-08-01 00:00:00", "price": 91.04},
            )


if __name__ == "__main__":
    unittest.main()
