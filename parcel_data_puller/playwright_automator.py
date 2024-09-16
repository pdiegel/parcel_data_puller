import asyncio
from playwright.async_api import (
    async_playwright,
    BrowserContext,
    Page,
    Locator,
)
import logging
from typing import Tuple, Dict, List, Any
from .helpers.misc_url_funcs import generate_direct_url


async def run_automation(
    url: str,
    actions: List[Dict[str, str]],
    parcel_data: Dict[str, str],
    context: BrowserContext,
) -> str:
    page = await context.new_page()
    await page.goto(url)

    result = ""
    for action_dict in actions:
        for action, value in action_dict.items():
            result, page = await execute_action(
                page, action, value, result, parcel_data, context
            )

    await context.close()
    if isinstance(result, Locator):
        raise ValueError("Window URL not found")
    return result


async def execute_action(
    page: Page,
    action: str,
    value: str,
    previous_value: str | Locator,
    parcel_data: Dict[str, str],
    context: BrowserContext,
) -> Tuple[str | Locator, Page]:
    element = previous_value
    value = format_parcel_value(value, parcel_data)

    try:
        if action == "FIND_BY_ID":
            element = page.locator(f"#{value}")
            return element, page
        elif action == "FIND_INPUT_BY_TEXT":
            element = page.locator(f"//input[@value='{value}']").first
        elif action == "FIND_BY_TEXT":
            element = page.get_by_text(value).first
        elif action == "FIND_BY_TYPE":
            # type is a, td, tr, etc.
            element = page.locator(f"{value}").first
        elif action == "FIND_BY_CLASS":
            element = page.locator(f".{value}").first
        elif action == "ENTER_TEXT":
            if not isinstance(element, Locator):
                raise ValueError("ENTER_TEXT action requires an element")
            await element.fill(value)
        elif action == "CLICK":
            if not isinstance(element, Locator):
                raise ValueError("CLICK action requires an element")
            await element.click()
        elif action == "WAIT_FOR_NEW_WINDOW":
            await page.wait_for_event("popup")  # type: ignore
        elif action == "SWITCH_WINDOW":
            pages = context.pages
            if len(pages) > 1:
                page = pages[-1]
                return element, page
        elif action == "RETURN" and value == "WINDOW_URL":
            logging.debug(f"Returning window URL: {page.url}")
            return page.url, page
    except Exception as e:
        logging.error(f"Error executing action '{action}': {str(e)}")
        raise

    return element, page


def format_parcel_value(value: str, parcel_data: Dict[str, str]) -> str:
    for key, dict_value in parcel_data.items():
        placeholder = f"[{key}]"
        if value and placeholder in value:
            return value.replace(placeholder, str(dict_value))
    return value


async def process_actions(
    url_info: Dict[str, Any],
    parcel_data: Dict[str, str],
):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)

        routines = [
            run_automation(
                generate_direct_url(url["TEMPLATE"], parcel_data),
                url["ACTIONS"],
                parcel_data,
                await browser.new_context(),
            )
            for url in url_info.values()
        ]
        results = await asyncio.gather(*routines)

        await browser.close()
        logging.info(f"Completed successfully: {results}")
        return results


if __name__ == "__main__":
    actions = [
        {"FIND_BY_ID": "ctl00_ContentPlaceHolder1_RadTextBook"},
        {"ENTER_TEXT": "[DEED_BOOK]"},
        {"FIND_BY_ID": "ctl00_ContentPlaceHolder1_RadTextPage"},
        {"ENTER_TEXT": "[DEED_PAGE]"},
        {"FIND_BY_ID": "ContentPlaceHolder1_btnExtSearch"},
        {"CLICK": ""},
        {
            "FIND_BY_ID": "\
ctl00_ContentPlaceHolder1_RadGridResults_ctl00_ctl04_gbcDocument"
        },
        {"CLICK": ""},
        {"WAIT_FOR_NEW_WINDOW": ""},
        {"SWITCH_WINDOW": ""},
        {"RETURN": "WINDOW_URL"},
    ]
    parcel_data = {"DEED_BOOK": "014846", "DEED_PAGE": "01590"}
    url_info = {
        "DEED": {
            "TEMPLATE": "https://rodcrpi.wakegov.com/\
Booksweb/GenExtSearch.aspx",
            "ACTIONS": actions,
        }
    }

    template = "https://rodcrpi.wakegov.com/Booksweb/GenExtSearch.aspx"

    logging.basicConfig(level=logging.INFO)
    results = asyncio.run(process_actions(url_info, parcel_data))
    logging.info(results)
