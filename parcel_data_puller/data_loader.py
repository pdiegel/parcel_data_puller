import yaml
import logging
from pathlib import Path
from typing import Dict, List, Union, Optional

StepType = Dict[
    str, Union[str, Optional[Dict[str, str]], List[Dict[str, Union[str, None]]]]
]
OrderType = List[StepType]
FieldMappingType = Dict[str, str]
CountyType = Dict[str, Union[str, OrderType, FieldMappingType]]

# Overall type hint for the output
CountyProcessingOrderType = Dict[str, List[CountyType]]


class ParcelDataLoader:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = self.load_config()
        logging.info(f"Loaded config from {config_path}")

    def load_config(
        self,
    ) -> CountyProcessingOrderType:
        with open(self.config_path, "r") as file:
            yaml_data = yaml.safe_load(file)
            logging.debug(
                f"Loaded config: {yaml_data} (type: {type(yaml_data)})"
            )
            return yaml_data

    def get_county_names(self) -> List[str]:
        county_names: List[str] = []
        for county in self.config.get("COUNTY_PROCESSING_ORDER", {}):
            if not isinstance(county, dict):
                continue
            logging.debug(f"County: {county.get('COUNTY', '')}")
            county_name = county.get("COUNTY", "")
            if not isinstance(county_name, str):
                continue
            county_names.append(county_name)

        return county_names

    def get_config_for(self, county_name: str) -> CountyType:
        county_configs = self.config.get("COUNTY_PROCESSING_ORDER")
        if not county_configs:
            logging.info("No county config found.")
            return {}
        for county_config in county_configs:
            if not isinstance(county_config, dict):  # type: ignore
                logging.info(f"Invalid county config: {county_config}")
                continue
            if county_config.get("COUNTY", "") == county_name:
                logging.debug(
                    f"Found config for {county_name}: {county_config}"
                )
                return county_config

        return {}

    def get_field_mapping_for(self, county_name: str) -> FieldMappingType:
        field_mapping = self.get_config_for(county_name).get("FIELD_MAPPING")
        if not field_mapping or not isinstance(field_mapping, dict):
            logging.info(f"Field mapping for {county_name} not found.")
            return {}

        logging.debug(f"Field mapping for {county_name}: {field_mapping}")
        return field_mapping

    def get_step_order_for(self, county_name: str) -> OrderType:
        step_order = self.get_config_for(county_name).get("ORDER")
        if not step_order or not isinstance(step_order, list):
            logging.info(f"Step order for {county_name} not found.")
            return []

        logging.debug(f"Step order for {county_name}: {step_order}")
        return step_order
