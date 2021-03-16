from selene.core import query
from selene.core.entity import Element
from selene.support.conditions import have
from selene.support.shared import config
from selenium.webdriver.common.keys import Keys

JS_CLICK = "arguments[0].click();"


def extract_text(elements: []) -> []:
    return [el.get(query.text) for el in elements]


def extract_titles(elements: []) -> []:
    return [el.get(query.attribute("title")) for el in elements]


def is_input_disabled(input_element: Element) -> bool:
    return input_element.matching(have.css_class("ant-input-disabled"))


def clear_text_input(input_element: Element) -> Element:
    return input_element.press(Keys.CONTROL + "A").press(Keys.BACKSPACE)


def reduce_timeout_decorator(func):
    def wrapper(*args, **kwargs):
        existing_implicit_wait = config.timeout
        config.timeout = 2
        func(*args, **kwargs)
        config.timeout = existing_implicit_wait

    return wrapper
