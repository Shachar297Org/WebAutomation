from selene.core import query


def extract_text(elements: []) -> []:
    return [el.get(query.text) for el in elements]

