from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from typing import Dict, List, Union
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options


class SeleniumAutomator:
    ACTIONS_THAT_RETURN_VALUES = ["WAIT_FOR_ID", "FIND_BY_ID", "RETURN"]

    def __init__(
        self,
        options: webdriver.ChromeOptions = Options(),
    ):
        self.driver = webdriver.Chrome(options=options)
        self.parcel_data: Dict[str, str] = dict()

    def execute_action(
        self,
        action: str,
        value: str = "",
        previous_value: Union[str, WebElement] = "",
    ) -> Union[str, WebElement]:
        element = previous_value
        value = self.format_parcel_value(value)
        if action == "WAIT_FOR_ID":
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, value))
            )
        elif action == "FIND_BY_ID":
            element = self.driver.find_element(By.ID, value)
        elif action == "ENTER_TEXT":
            if not isinstance(element, WebElement):
                raise ValueError("ENTER_TEXT action requires a WebElement")
            element.clear()
            element.send_keys(value)
        elif action == "CLICK":
            if not isinstance(element, WebElement):
                raise ValueError("CLICK action requires a WebElement")
            element.click()
        elif action == "WAIT_FOR_NEW_WINDOW":
            WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))
        elif action == "SWITCH_WINDOW":
            self.driver.switch_to.window(self.driver.window_handles[1])
        elif action == "RETURN" and value == "WINDOW_URL":
            window_url = self.driver.current_url
            for _ in self.driver.window_handles:
                if len(self.driver.window_handles) > 1:
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    self.driver.close()

            self.driver.switch_to.window(self.driver.window_handles[0])
            self.driver.get("about:blank")
            return window_url
        return element

    def process_actions(
        self,
        template: str,
        actions: List[Dict[str, str]],
        parcel_data: Dict[str, str],
    ) -> Union[str, WebElement, None]:
        self.set_parcel_data(parcel_data)
        result = ""
        self.driver.get(template)
        # self.driver.minimize_window()
        for action_dict in actions:
            for action, value in action_dict.items():
                result = self.execute_action(action, value, result)
                if action == "RETURN" and value == "WINDOW_URL":
                    return result
        return result

    def set_parcel_data(self, parcel_data: Dict[str, str]):
        self.parcel_data = parcel_data

    def format_parcel_value(self, value: str) -> str:
        for key, dict_value in self.parcel_data.items():
            placeholder = f"[{key}]"
            if value and placeholder in value:
                return value.replace(placeholder, str(dict_value))
        return value
