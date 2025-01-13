
import os
import time
from typing import Union

import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from fake_useragent import UserAgent

from .logger_config import Logger, get_logger


class GenericDriver(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.browser_name = str(kwargs.get('browser', 'chrome')).lower()
        self.logger: Logger = self.get_logger()

        self.base_path = os.path.dirname(__file__)
        self.start_driver()

    def get_logger(self) -> Logger:
        return get_logger("GenericDriver", log_to_console=True, log_to_file="./GenericDriver.log")

    def start_driver(self):
        if self.browser_name == 'chrome':
            # chromedriver_autoinstaller.install()
            extens_path = os.path.join(self.base_path, 'driver\\extensions\\websigner_2.14.3_0.crx')
            userdt_path = os.path.join(self.base_path, 'driver\\user_data')
            driver_path = os.path.join(self.base_path, 'driver\\chromedriver.exe')

            self.driver_opts = webdriver.ChromeOptions()
            self.driver_opts.add_extension(extens_path)

            self.driver_opts.add_experimental_option('excludeSwitches', ['enable-logging'])

            ua = UserAgent()
            userAgent = ua.random
            self.driver_opts.add_argument(f'user-agent={userAgent}')
            self.driver_opts.add_argument(f"user-data-dir={userdt_path}")
            self.driver_opts.add_argument("--enable-javascript")
            self.driver_opts.add_argument("--start-maximized")
            if self.kwargs.get('headless', False):
                self.driver_opts.add_argument('--headless')

            self.driver = webdriver.Chrome(driver_path, options=self.driver_opts)

        else:
            raise NotImplementedError(f"browser name {self.browser_name} not recognized try: chrome")

    def reset_driver(self):
        self.driver.quit()
        self.start_driver()

    def run(self) -> bool:
        try:
            self.logger.info(' -- Start Params -- ')
            self.logger.info(f"Loading {type(self).__name__}")
            self.logger.info(f"Browser defined to: {self.browser_name}")
            self.logger.info(' -- Done Params -- ')

            self.logger.info('-- Start Prepare --')
            self.prepare()
            self.logger.info('-- Done Prepare --')

            self.logger.info('-- Start Scraping --')
            self.scrape()
            self.logger.info('-- Done Scraping --')

            self.logger.info('-- Start Transform --')
            self.transform()
            self.logger.info('-- Done Transform --')
            return True

        except Exception as e:
            self.logger.error(e, exc_info=True)
            return False

        finally:
            self.driver.quit()

    def prepare(self):
        raise NotImplementedError

    def scrape(self):
        raise NotImplementedError

    def transform(self):
        raise NotImplementedError

    def get_element_xpath(self, xpath: str, parent: Union[WebElement, None] = None) -> WebElement:
        try:
            if parent is None:
                return self.driver.find_element_by_xpath(xpath)
            return parent.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return None

    def get_element_text_xpath(self, xpath: str, parent: Union[WebElement, None] = None) -> str:
        try:
            if parent is None:
                return self.driver.find_element_by_xpath(xpath).text
            return parent.find_element_by_xpath(xpath).text
        except NoSuchElementException:
            return ''

    def get_elements_xpath(self, xpath: str, parent: Union[WebElement, None] = None) -> list[WebElement]:
        try:
            if parent is None:
                return self.driver.find_elements_by_xpath(xpath)
            return parent.find_elements_by_xpath(xpath)
        except NoSuchElementException:
            return []

    def get_elements_text_xpath(self, xpath: str, parent: Union[WebElement, None] = None) -> list[str]:
        try:
            if parent is None:
                return [element.text for element in self.driver.find_elements_by_xpath(xpath)]
            return [sub.text for sub in parent.find_elements_by_xpath(xpath)]
        except NoSuchElementException:
            return ['']

    def click_on_element(self, element):
        try:
            ActionChains(self.driver).move_to_element(element).perform()
            element.click()
            return True
        except WebDriverException:
            return False

    def wait_for_downloads(self, download_folder):
        while any([filename.endswith(".crdownload") for filename in os.listdir(download_folder)]):
            time.sleep(0.1)
        time.sleep(0.02)
