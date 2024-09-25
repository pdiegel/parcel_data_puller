from typing import Dict
import logging


def generate_direct_url(url: str, parcel_data: Dict[str, str]) -> str:
    logging.debug(f"Generating direct URL for {url}")
    logging.debug(f"Data: {parcel_data}")
    for key, _ in parcel_data.items():
        placeholder = f"[{key}]"
        parcel_value = str(parcel_data.get(key, ""))

        if placeholder in url:
            logging.debug(f"Replacing {placeholder} with {parcel_value}")
            url = url.replace(placeholder, parcel_value)
    return url
