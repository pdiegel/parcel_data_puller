import requests
from bs4 import BeautifulSoup
import logging
from .data_loader import ParcelDataLoader
from typing import Dict
from urllib.parse import urljoin
import time
import asyncio
from .playwright_automator import process_actions
from .helpers.misc_url_funcs import generate_direct_url


class CountyURLManager:
    def __init__(self, data_loader: ParcelDataLoader):
        self.data_loader = data_loader

    def get_urls_for_county(
        self, county_name: str, parcel_data: Dict[str, str]
    ) -> Dict[str, str] | Dict[None, None]:
        county_url_config: Dict[str, Dict[str, str]] = (
            self.data_loader.get_county_url_config(county_name)
        )
        if not county_url_config:
            logging.error(f"No URL template found for county: {county_name}")
            return {}

        county_urls: Dict[str, str] = dict()
        playwright_url_data: Dict[str, Dict[str, str]] = {}

        for url_name, url_info in county_url_config.items():
            url_type = url_info.get("TYPE")
            url = generate_direct_url(url_info["TEMPLATE"], parcel_data)

            if url_type == "DIRECT":
                pass
            elif url_type == "SCRAPE":
                url = self.scrape_url(
                    url,
                    parcel_data,
                    url_info.get("LINK_SELECTOR"),
                )
            elif url_type == "PLAYWRIGHT":
                playwright_url_data[url_name] = url_info
            else:
                logging.error(
                    f"Unknown URL type '{url_type}' for county: {county_name}"
                )
                continue

            if url:
                county_urls[url_name] = url

        if playwright_url_data:
            start = time.perf_counter()
            playwright_results = asyncio.run(
                process_actions(playwright_url_data, parcel_data)
            )
            end = time.perf_counter()
            logging.info(
                f"Time taken for Playwright Task {county_name}: {end - start}"
            )
            for url_name, result in zip(
                playwright_url_data.keys(), playwright_results
            ):
                county_urls[url_name] = result
        return county_urls

    def scrape_url(
        self, template: str, data: Dict[str, str], link_selector: str | None
    ) -> str:
        url = generate_direct_url(template, data)
        if not link_selector:
            return ""
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError as e:
            logging.error(f"Failed to retrieve page: {url}, {str(e)}")
            return ""

        if response.status_code != 200:
            logging.error(f"Failed to retrieve page: {url}")
            return ""

        soup = BeautifulSoup(response.text, "html.parser")

        link = soup.select_one(link_selector)
        if not link or not link.get("href"):
            logging.error(f"Failed to find link on page: {url}")
            return ""

        return urljoin(url, link["href"])  # type: ignore
