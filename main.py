from parcel_data_puller.aggregator import ParcelDataAggregator
from parcel_data_puller.url_manager import CountyURLManager
from config.constants import YAML_CONFIG_PATH
import logging

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        filename="logs/parcel_data_puller.log",
        filemode="w",
    )
    aggregator = ParcelDataAggregator(YAML_CONFIG_PATH)
    api_data = aggregator.aggregate_for_county(
        "WAKE", where_clause="PARCEL_ID=0064907", num_records=5
    )
    # api_data = aggregator.aggregate_for_county(
    #     "JOHNSTON", where_clause="PARCEL_ID='164504-60-3696'", num_records=5
    # )
    logging.info(api_data)

    county_url_manager: CountyURLManager = CountyURLManager(
        aggregator.data_loader
    )
    if api_data[0]:
        county_urls = county_url_manager.get_urls_for_county(
            "WAKE", api_data[0]
        )
        logging.info(county_urls)
        for url in county_urls:
            api_data[0][url] = county_urls[url]

    logging.info(api_data)
