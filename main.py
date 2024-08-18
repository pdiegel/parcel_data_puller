from parcel_data_puller.aggregator import ParcelDataAggregator
from parcel_data_puller.url_manager import CountyURLManager
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
    api_data = aggregator.aggregate_for_county(
        "WAKE", where_clause="PARCEL_ID=0007561", num_records=5
    )
    print(api_data)

    county_url_manager = CountyURLManager(aggregator.data_loader)
    if api_data[0]:
        county_urls = county_url_manager.get_urls_for_county(
            "WAKE", api_data[0]
        )
        print(county_urls)
