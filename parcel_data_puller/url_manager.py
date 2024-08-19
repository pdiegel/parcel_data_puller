import requests
from bs4 import BeautifulSoup
import logging
from .data_loader import ParcelDataLoader
from typing import Dict
from urllib.parse import urljoin
from .selenium_automator import SeleniumAutomator
from selenium.webdriver.chrome.options import Options


class CountyURLManager:
    CHROME_OPTIONS = Options()
    CHROME_OPTIONS.add_argument("--log-level=3")  # type: ignore
    # Make the window size as small as possible
    # CHROME_OPTIONS.add_argument("--window-size=500,500")  # type: ignore

    def __init__(self, data_loader: ParcelDataLoader):
        self.data_loader = data_loader
        self.selenium_automator = SeleniumAutomator(self.CHROME_OPTIONS)

    def get_urls_for_county(
        self, county_name: str, parcel_data: Dict[str, str]
    ) -> Dict[str, str]:
        county_url_config: Dict[str, Dict[str, str]] = (
            self.data_loader.get_county_url_config(county_name)
        )
        if not county_url_config:
            raise ValueError(f"No URL template found for county: {county_name}")

        county_urls: Dict[str, str] = dict()

        for url_name, url_info in county_url_config.items():
            url_type = url_info.get("TYPE", "DIRECT")
            if url_type == "DIRECT":
                url = self._generate_direct_url(
                    url_info["TEMPLATE"], parcel_data
                )

            elif url_type == "SCRAPE":
                url = self._scrape_url(
                    url_info["TEMPLATE"],
                    parcel_data,
                    url_info.get("LINK_SELECTOR"),
                )
            elif url_type == "SELENIUM":
                url = self._scrape_selenuim_url(
                    url_info["TEMPLATE"], url_info.get("ACTIONS"), parcel_data
                )

            else:
                raise ValueError(
                    f"Unknown URL type '{url_type}' for county: {county_name}"
                )
            county_urls[url_name] = url

        return county_urls

    def _generate_direct_url(self, template: str, data: Dict[str, str]) -> str:
        for key, value in data.items():
            placeholder = f"[{key}]"
            template = template.replace(placeholder, str(value))
        return template

    def _scrape_url(
        self, template: str, data: Dict[str, str], link_selector: str | None
    ) -> str:
        url = self._generate_direct_url(template, data)
        if not link_selector:
            return url
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError(f"Failed to retrieve page: {url}")

        soup = BeautifulSoup(response.text, "html.parser")

        link = soup.select_one(link_selector)
        if not link or not link.get("href"):
            raise ValueError(f"Failed to find link on page: {url}")

        return urljoin(url, link["href"])

    def _scrape_selenuim_url(
        self,
        template: str,
        actions: list[Dict[str, str]],
        parcel_data: Dict[str, str],
    ) -> str:
        return self.selenium_automator.process_actions(
            template, actions, parcel_data
        )  # type: ignore
