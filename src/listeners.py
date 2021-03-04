import logging

from selene.core.entity import Element
from selenium.webdriver.support.abstract_event_listener import AbstractEventListener


class DriverEventListener(AbstractEventListener):
    def before_navigate_to(self, url, driver):
        logging.info("Navigate to " + url)

    def before_find(self, by, value, driver):
        logging.info("Find element by " + by + " " + value)

    def before_click(self, element, driver):
        logging.info("Click on element " + element.__str__())

    def before_change_value_of(self, element: Element, driver):
        print("Set value for " + element.__str__())

    def before_execute_script(self, script, driver):
        print("Execute script: " + script)