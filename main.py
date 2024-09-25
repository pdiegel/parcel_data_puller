from parcel_data_puller.processor import ParcelProcessor
from parcel_data_puller.data_loader import ParcelDataLoader
from config.constants import YAML_CONFIG_PATH
import logging
from typing import Dict
import json


def get_county_data(county: str, parcel_id: str) -> Dict[str, str]:
    data_loader = ParcelDataLoader(YAML_CONFIG_PATH)
    processor = ParcelProcessor(
        data_loader,
        county,
        where_clause=f"PARCEL_ID='{parcel_id}'",
        num_records=5,
    )
    parcel_data = {}
    for i, step_details in enumerate(data_loader.get_step_order_for(county)):
        logging.debug(f"parcel data before step {i + 1}: {parcel_data}")
        parcel_data = processor.process_step(step_details, parcel_data)
        logging.debug(f"parcel data after step {i + 1}: {parcel_data}")

    if parcel_data:
        return parcel_data
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
