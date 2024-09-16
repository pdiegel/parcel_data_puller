from .query import ParcelQuery
import logging
from .data_loader import ParcelDataLoader
from typing import List, Dict
import re


class ParcelProcessor:

    def __init__(
        self,
        data_loader: ParcelDataLoader,
        county_name: str,
        where_clause: str = "1=1",
        num_records: int = 50,
    ):
        self.data_loader = data_loader
        self.county_name = county_name
        self.where_clause = where_clause
        self.num_records = num_records

    def process(self) -> List[None] | List[Dict[str, str]]:
        url = self.data_loader.get_county_url(self.county_name)
        field_map = self.data_loader.get_field_mappings(self.county_name)

        if not url or not field_map:
            logging.info(f"Data for {self.county_name} not available.")
            return []

        query = ParcelQuery(url, field_map)
        results = query.query(self.where_clause, self.num_records)
        results = self.process_additional_data(results)  # type: ignore
        logging.info(f"Processed {len(results)} records for {self.county_name}")
        return results

    def process_additional_data(
        self, results: List[Dict[str, str]] | List[None]
    ) -> List[Dict[str, str]] | List[None]:
        if len(results) == 0:
            return results

        additional_processing_config = (
            self.data_loader.get_county_additional_processing_config(
                self.county_name
            )
        )
        for key, value in additional_processing_config.items():
            regex = value["REGEX"]
            for result in results:

                source = str(result[value["SOURCE"]])  # type: ignore
                result[key] = self.get_regex_match(  # type: ignore
                    regex,
                    source,  # type: ignore
                )
        return results

    def get_regex_match(self, regex: str, source: str) -> str:
        logging.info(f"Searching for {regex} in {source}")
        match = re.search(regex, source)
        if match:
            logging.info(f"Found match: {match.group(1)}")
            return match.group(1)
        return ""
