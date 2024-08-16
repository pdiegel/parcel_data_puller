import requests
import logging
from typing import Dict, List


class ParcelQuery:
    def __init__(self, url: str, field_map: Dict[str, str]):
        self.url = url
        self.field_map = field_map

    def query(
        self,
        where_clause: str = "1=1",
        num_records: int = 50,
    ) -> List[None] | List[Dict[str, str]]:
        params = {
            "where": self.format_where_clause(where_clause),
            "outFields": ",".join(self.field_map.values()),
            "f": "geojson",
            "resultRecordCount": num_records,
        }
        all_results: List[None] | List[Dict[str, str]] = []

        logging.debug(f"Querying {self.url} with params: {params}")
        response = requests.get(self.url, params=params)

        if response.status_code == 200:
            data = response.json()
            features = data.get("features", [])
            logging.debug(f"Received {len(features)} features")

            for feature in features:
                all_results.append(self.process_feature(feature))

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

    def format_where_clause(self, where_clause: str) -> str:
        tokenized_where_clause = where_clause.split("=")
        standardized_field = tokenized_where_clause[0]
        standardized_fields = self.field_map.keys()

        if standardized_field not in standardized_fields:
            logging.error(
                f"Field {standardized_field} not found in field map: \
{standardized_fields}"
            )
            return where_clause

        layer_specific_field = self.field_map[standardized_field]
        return f"{layer_specific_field}={tokenized_where_clause[1]}"
