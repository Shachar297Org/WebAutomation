from selene.core import query

JS_CLICK = "arguments[0].click();"


def extract_text(elements: []) -> []:
    return [el.get(query.text) for el in elements]

