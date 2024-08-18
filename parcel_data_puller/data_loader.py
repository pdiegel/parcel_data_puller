import yaml
import logging
from pathlib import Path
from typing import Dict


class ParcelDataLoader:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = self.load_config()
        logging.info(f"Loaded config from {config_path}")

    def load_config(
        self,
    ) -> (
        Dict[str, Dict[str, str]]
        | Dict[str, Dict[str, bool]]
        | Dict[str, Dict[str, Dict[str, str]]]
    ):
        with open(self.config_path, "r") as file:
            yaml_data = yaml.safe_load(file)
            logging.debug(
                f"Loaded config: {yaml_data} (type: {type(yaml_data)})"
            )
            return yaml_data

    def get_county_url(self, county_name: str) -> str:
        county_url = self.config.get("COUNTY_URLS", {}).get(county_name)
        if not county_url or not isinstance(county_url, str):
            logging.info(f"County URL for {county_name} not found.")
            raise ValueError(f"County URL for {county_name} not found.")

        logging.debug(f"County URL for {county_name}: {county_url}")
        return county_url

    def get_field_mappings(self, county_name: str) -> Dict[str, str]:
        field_mappings = self.config.get("COUNTY_FIELD_MAPPING", {}).get(
            county_name
        )
        if not field_mappings or not isinstance(field_mappings, dict):
            logging.info(f"Field mappings for {county_name} not found.")
            raise ValueError(f"Field mappings for {county_name} not found.")

        logging.debug(f"Field mappings for {county_name}: {field_mappings}")
        return field_mappings

    def get_county_url_config(
        self, county_name: str
    ) -> Dict[str, Dict[str, str]]:
        county_config = self.config.get("COUNTY_URL_MAPPING", {}).get(
            county_name
        )
        logging.debug(f"County config for {county_name}: {county_config}")
        if not county_config or not isinstance(county_config, dict):
            logging.info(f"County config for {county_name} not found.")
            raise ValueError(f"County config for {county_name} not found.")

        logging.debug(f"County config for {county_name}: {county_config}")
        return county_config
