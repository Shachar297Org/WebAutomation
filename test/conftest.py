import os

import allure
from allure_commons.types import AttachmentType
from selene.support.shared import browser


browser.config.timeout = int(os.getenv('SELENE_TIMEOUT'))
browser.config.browser_name = os.getenv('SELENE_BROWSER_NAME')
browser.config.base_url = os.getenv('SELENE_BASE_URL')
browser.config.hold_browser_open = os.getenv('SELENE_HOLD_BROWSER_OPEN')


def pytest_exception_interact(node, call, report):

    allure.attach(body=browser.driver.get_screenshot_as_png(), name="Screenshot",
                  attachment_type=AttachmentType.PNG, extension='.png')
