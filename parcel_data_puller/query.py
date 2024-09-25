import requests
import logging
from typing import Dict


class ParcelQuery:
    def __init__(self, url: str, field_map: Dict[str, str]):
        self.url = url
        self.field_map = field_map

    def query(
        self,
        where_clause: str = "1=1",
        num_records: int = 50,
    ) -> Dict[str, str]:
        params = {  # type: ignore
            "where": self.format_where_clause(where_clause),
            "outFields": ",".join(self.field_map.values()),
            "f": "geojson",
            "resultRecordCount": num_records,
        }
        results: Dict[str, str] = {}

        logging.debug(f"Querying {self.url} with params: {params}")
        try:
            response = requests.get(self.url, params=params)  # type: ignore
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
            return {}
        except requests.exceptions.ConnectionError as conn_err:
            logging.error(f"Connection error occurred: {conn_err}")
            return {}
        except requests.exceptions.Timeout as timeout_err:
            logging.error(f"Timeout error occurred: {timeout_err}")
            return {}
        except requests.exceptions.RequestException as req_err:
            logging.error(f"An error occurred: {req_err}")
            return {}

        if response.status_code == 200:
            data = response.json()
            features = data.get("features", [])
            logging.debug(f"Received {len(features)} features")

            for feature in features:
                processed_feature = self.process_feature(feature)
                results.update(processed_feature)
        else:
            logging.error(f"Received status code {response.status_code}")
            return {}

        return results

    def process_feature(
        self, feature: Dict[str, Dict[str, str]]
    ) -> Dict[str, str]:
        return {
            standardized_name: feature["properties"][original_name]
            for standardized_name, original_name in self.field_map.items()
        }

    def format_where_clause(self, where_clause: str) -> str:
        for standardized_field, layer_specific_field in self.field_map.items():
            if standardized_field not in where_clause:
                continue
            where_clause = where_clause.replace(
                standardized_field, layer_specific_field
            )

        return where_clause
