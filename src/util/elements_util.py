from selene.core import query
from selene.support.shared import config

JS_CLICK = "arguments[0].click();"


def extract_text(elements: []) -> []:
    return [el.get(query.text) for el in elements]


def extract_titles(elements: []) -> []:
    return [el.get(query.attribute("title")) for el in elements]


def reduce_timeout_decorator(func):
    def wrapper(*args, **kwargs):
        existing_implicit_wait = config.timeout
        config.timeout = 2
        func(*args, **kwargs)
        config.timeout = existing_implicit_wait
    return wrapper
