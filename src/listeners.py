import logging

from selene.core.entity import Element
from selenium.webdriver.support.abstract_event_listener import AbstractEventListener


class DriverEventListener(AbstractEventListener):
    def before_navigate_to(self, url, driver):
        logging.debug("Navigate to " + url)

    def before_find(self, by, value, driver):
        logging.debug("Find element by " + by + " " + value)

    def before_click(self, element, driver):
        logging.debug("Click on element " + element.__str__())

    def before_change_value_of(self, element: Element, driver):
        logging.debug("Set value for " + element.__str__())

    def before_execute_script(self, script, driver):
        logging.debug("Execute script: " + script)
