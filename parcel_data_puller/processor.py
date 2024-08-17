from .query import ParcelQuery
import logging
from .data_loader import ParcelDataLoader
from typing import List, Dict


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
        logging.info(f"Processed {len(results)} records for {self.county_name}")
        return results
