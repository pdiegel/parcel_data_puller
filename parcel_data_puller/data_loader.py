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
        county_url = self.config.get("county_urls", {}).get(county_name)
        if not county_url or not isinstance(county_url, str):
            logging.info(f"County URL for {county_name} not found.")
            raise ValueError(f"County URL for {county_name} not found.")

        logging.debug(f"County URL for {county_name}: {county_url}")
        return county_url

    def get_field_mappings(self, county_name: str) -> Dict[str, str]:
        field_mappings = self.config.get("field_mappings", {}).get(county_name)
        if not field_mappings or not isinstance(field_mappings, dict):
            logging.info(f"Field mappings for {county_name} not found.")
            raise ValueError(f"Field mappings for {county_name} not found.")

        logging.debug(f"Field mappings for {county_name}: {field_mappings}")
        return field_mappings