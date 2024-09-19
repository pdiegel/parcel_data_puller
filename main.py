from parcel_data_puller.aggregator import ParcelDataAggregator
from parcel_data_puller.processor import ParcelProcessor
from parcel_data_puller.url_manager import CountyURLManager
from parcel_data_puller.data_loader import ParcelDataLoader
from config.constants import YAML_CONFIG_PATH
import logging
from typing import Dict
import json


def get_county_data(county: str, parcel_id: str) -> Dict[str, str]:
    processor = ParcelProcessor(
        ParcelDataLoader(YAML_CONFIG_PATH),
        county,
    )
    aggregator = ParcelDataAggregator(YAML_CONFIG_PATH)
    api_data = aggregator.aggregate_for_county(
        county, where_clause=f"PARCEL_ID='{parcel_id}'", num_records=5
    )

    logging.info(api_data)

    county_url_manager: CountyURLManager = CountyURLManager(
        aggregator.data_loader
    )
    if api_data[0]:

        county_urls = county_url_manager.get_urls_for_county(
            county, api_data[0]
        )
        logging.info(county_urls)
        for url in county_urls:
            api_data[0][url] = county_urls[url]  # type: ignore

        logging.info(api_data)
        processor.process_post_web_data(api_data)
        logging.info(api_data)
        return api_data[0]
    return {}


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        filename="logs/parcel_data_puller.log",
        filemode="w",
    )

    county_data = get_county_data("WAKE", "0113335")
    # county_data = get_county_data("JOHNSTON", "176000-51-7806")
    # county_data = get_county_data("JOHNSTON", "176000-13-0450")
    # county_data = get_county_data("JOHNSTON", "167700-38-9625")
    # county_data = get_county_data("DURHAM", "108400")
    print(county_data)
    # write to json for easier reading
    with open("test-run.json", "w") as f:
        json.dump(county_data, f, indent=4)
