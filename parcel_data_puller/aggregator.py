from .data_loader import ParcelDataLoader
from .processor import ParcelProcessor
from pathlib import Path
import logging


class ParcelDataAggregator:
    def __init__(
        self,
        config_path: Path,
    ):
        self.data_loader = ParcelDataLoader(config_path)

    def aggregate_for_county(
        self,
        county_name: str,
        where_clause: str = "1=1",
        num_records: int = 50,
    ):
        processor = ParcelProcessor(
            self.data_loader,
            county_name,
            where_clause,
            num_records,
        )
        results = processor.process()

        if not results:
            logging.info(f"No results were returned for {county_name}.")
            return

        logging.info(f"Results for {county_name}:")
        for result in results:
            logging.debug(result)
