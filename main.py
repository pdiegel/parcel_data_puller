from parcel_data_puller.aggregator import ParcelDataAggregator
import logging
from pathlib import Path

if __name__ == "__main__":
    YAML_CONFIG_PATH = Path("config/field_mappings.yaml")
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        filename="logs/parcel_data_puller.log",
    )
    aggregator = ParcelDataAggregator(YAML_CONFIG_PATH)
    aggregator.aggregate_for_county("Wake")
