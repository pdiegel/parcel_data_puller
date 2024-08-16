import requests
import logging
from typing import Dict, List


class ParcelQuery:
    def __init__(self, url: str, field_map: Dict[str, str]):
        self.url = url
        self.field_map = field_map
        self.result_record_count = 50

    def query(self) -> List[None] | List[Dict[str, str]]:
        params = {
            "where": "1=1",
            "outFields": ",".join(self.field_map.values()),
            "f": "geojson",
            "resultRecordCount": self.result_record_count,
            "resultOffset": 0,
        }
        all_results: List[None] | List[Dict[str, str]] = []

        response = requests.get(self.url, params=params)
        if response.status_code == 200:
            data = response.json()
            features = data.get("features", [])
            logging.debug(f"Received {len(features)} features")
            logging.debug(features[0])
            logging.debug(f"features are of type {type(features[0])}")

            for feature in features:
                all_results.append(self.process_feature(feature))

            if len(features) < self.result_record_count:
                return all_results

            params["resultOffset"] += self.result_record_count  # type: ignore
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return []

        return all_results

    def process_feature(
        self, feature: Dict[str, Dict[str, str]]
    ) -> Dict[str, str]:
        return {
            standardized_name: feature["properties"][original_name]
            for standardized_name, original_name in self.field_map.items()
        }
