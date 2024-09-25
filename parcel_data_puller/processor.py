from .query import ParcelQuery
import logging
from .data_loader import ParcelDataLoader, StepType
from .playwright_automator import process_actions
from .helpers.misc_url_funcs import generate_direct_url
from typing import Dict, List
import re
import asyncio


class ParcelProcessor:
    STEP_METHOD_MAP = {
        "SCRAPE": {
            "GIS_API": "scrape_gis_api",
            "PLAYWRIGHT": "scrape_playwright",
            "DIRECT": "scrape_direct",
        },
        "EXTRACT": {
            "REGEX": "extract_regex",
        },
    }

    def __init__(
        self,
        data_loader: ParcelDataLoader,
        county_name: str,
        where_clause: str = "1=1",
        num_records: int = 50,
    ):
        self.data_loader = data_loader
        self.county_name = county_name
        self.field_map = self.data_loader.get_field_mapping_for(county_name)
        self.where_clause = where_clause
        self.num_records = num_records

    def process_step(
        self, step_details: StepType, parcel_data: Dict[str, str] = {}
    ) -> Dict[str, str]:
        step = step_details.get("STEP", "")
        method = step_details.get("METHOD", "")
        step_methods = self.STEP_METHOD_MAP.get(step, {})  # type: ignore
        method_name: str = step_methods.get(method, "")  # type: ignore
        if not method_name:
            logging.error(f"Invalid method for step: {method}")
            return {}

        return getattr(self, method_name)(  # type: ignore
            step_details,
            parcel_data,
        )

    def scrape_gis_api(
        self, step_details: StepType, parcel_data: Dict[str, str]
    ) -> Dict[str, str]:
        url = generate_direct_url(
            step_details.get("URL", ""),  # type: ignore
            parcel_data,
        )
        query = ParcelQuery(url, self.field_map)
        parcel_data = query.query(self.where_clause, self.num_records)
        logging.info(
            f"Processed {len(parcel_data)} records for {self.county_name}"
        )
        return parcel_data

    def extract_regex(
        self,
        step_details: StepType,
        parcel_data: Dict[str, str],
    ) -> Dict[str, str]:

        new_field = step_details.get("FIELD", "")
        source_field = step_details.get("SOURCE", "")
        source = parcel_data.get(source_field, "")  # type: ignore
        regex = step_details.get("REGEX", "")

        logging.debug(f"parcel_data during extract_regex: {parcel_data}")
        regex_match = self.get_regex_match(regex, source)  # type: ignore
        if not regex_match:
            parcel_data[new_field] = ""  # type: ignore
        else:
            parcel_data[new_field] = self.get_regex_match(  # type: ignore
                regex,  # type: ignore
                source,  # type: ignore
            )
        return parcel_data

    def scrape_playwright(
        self, step_details: StepType, parcel_data: Dict[str, str]
    ) -> Dict[str, str]:
        url = generate_direct_url(
            step_details.get("URL", ""),  # type: ignore
            parcel_data,
        )

        actions = step_details.get("ACTIONS", [])
        if self.has_invalid_action(actions, parcel_data):  # type: ignore
            return parcel_data

        new_field = step_details.get("FIELD", "")

        playwright_results = asyncio.run(
            process_actions(
                url,
                actions,  # type: ignore
                parcel_data,
            )
        )
        for result in playwright_results:
            parcel_data[new_field] = result  # type: ignore

        return parcel_data

    def scrape_direct(
        self, step_details: StepType, parcel_data: Dict[str, str]
    ) -> Dict[str, str]:
        url = generate_direct_url(
            step_details.get("URL", ""),  # type: ignore
            parcel_data,
        )
        if not url:
            logging.error(f"Data for {self.county_name} not available.")
            return {}

        new_field = step_details.get("FIELD", "")
        parcel_data[new_field] = url  # type: ignore
        logging.info(f"Added {new_field} to parcel_data: {url}")
        return parcel_data

    def get_regex_match(self, regex: str, source: str) -> str:
        logging.info(f"Searching for {regex} in {source}")
        match = re.search(regex, source)
        if match:
            logging.info(f"Found match: {match.group(1)}")
            return match.group(1)
        return ""

    def has_invalid_action(
        self, actions: List[Dict[str, str]], parcel_data: Dict[str, str]
    ) -> bool:
        for action in actions:
            value = list(action.values())[0]  # type: ignore
            if not value:
                continue
            logging.debug(f"Checking action: {action}")
            logging.debug(f"Value: {value}")
            for key in parcel_data:
                if f"[{key}]" in value and not parcel_data[key]:
                    logging.error(f"Invalid key found in action: {key}")
                    return True
        return False
