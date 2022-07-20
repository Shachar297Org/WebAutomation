import os

import allure
import pytest
from allure_commons.types import AttachmentType
from selene.support.shared import browser, config
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.event_firing_webdriver import EventFiringWebDriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from src.util.driver_util import clear_session_storage, clear_local_storage
from src.listeners import DriverEventListener

config.timeout = int(os.getenv('SELENE_TIMEOUT', 5))
config.browser_name = os.getenv('SELENE_BROWSER_NAME', 'chrome')
config.base_url = os.getenv('SELENE_BASE_URL', 'https://web.int.lumenisx.lumenis.com')
config.hold_browser_open = os.getenv('SELENE_HOLD_BROWSER_OPEN')
remote = bool(os.getenv("SELENE_REMOTE", False))
chrome_headless = bool(os.getenv("SELENE_CHROME_HEADLESS", False))


@pytest.fixture(autouse=True, scope="session")
def setup_driver():
    print(config)
    if remote:
        driver = _get_remote_web_driver()
    else:
        if config.browser_name == 'chrome':
            driver = _get_chrome_driver()
        elif config.browser_name == 'firefox':
            driver = _get_firefox_driver()
        else:
            raise Exception(config.browser_name + " local browser run isn't supported by automation framework")
    config.driver = EventFiringWebDriver(driver, DriverEventListener())
    config.driver.set_window_size(1280, 720)
    yield
    browser.quit()


@pytest.fixture(autouse=True, scope="class")
def cleanup_browser_session():
    yield
    clear_session_storage()
    clear_local_storage()


def pytest_exception_interact(node, call, report):
    allure.attach(body=browser.driver.get_screenshot_as_png(), name="Screenshot",
                  attachment_type=AttachmentType.PNG, extension='.png')


def _get_remote_web_driver():
    return webdriver.Remote(
        command_executor='http://selenium-server-sample-url:4444/wd/hub',
        desired_capabilities={'browserName': config.browser_name,
                              'javascriptEnabled': True,
                              'enableVNC': True,
                              'enableVideo': False
                              })


def _get_chrome_driver():
    opt = Options()
    opt.headless = chrome_headless
    opt.add_argument("--no-sandbox")
    opt.add_argument("--disable-dev-shm-usage")

    return webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=opt)


def _get_firefox_driver():
    return webdriver.Chrome(executable_path=GeckoDriverManager().install())
