import time

from selene.core import query
from selene.support.conditions import be, have
from selene.support.conditions.be import not_
from selene.support.shared.jquery_style import s, ss


class SearchInput:
    def __init__(self, locator):
        self.input = s(locator)
        self.clear_icon = self.input.s("i.ant-input-clear-icon")

    def search(self, text: str):
        self.input.set_value(text)
        time.sleep(1)  # TODO workaround, replace with the waiter

    def clear(self):
        self.clear_icon.click()
        self.input.wait.until(be.empty)

    def is_empty(self) -> bool:
        return self.input.matching(be.blank)

    def get_text(self) -> str:
        return self.input.get(query.text)

    def get_placeholder(self) -> str:
        return self.input.get(query.attribute("placeholder"))


class SelectBox:
    def __init__(self, select_box_locator, items_locator):
        self.select = s(select_box_locator)
        self.items = ss(items_locator)

    def open(self):
        if not self.is_opened():
            self.select.click()
        return self

    def is_opened(self) -> bool:
        return self.select.matching(have.css_class("ant-select-open"))

    def is_empty(self) -> bool:
        return self.select.s(".ant-select-selection-selected-value").matching(not_.present)

    def select_item(self, item: str):
        self.open()
        self.items.filtered_by(have.text(item))[0].click()
        # self.select_box.s("//li[@role='option'][text()='{}']".format(item)).click()

    def get_selected_item(self) -> str:
        return self.select.s(".ant-select-selection-selected-value").get(query.text)

    def get_placeholder(self) -> str:
        return self.select.s(".ant-select-selection__placeholder").get(query.text)

    def get_label(self) -> str:
        return self.select.s("./ancestor::*[@class='ant-row ant-form-item']//label").get(query.text)

    def is_enabled(self) -> bool:
        return self.select.matching(be.enabled)


class TreeSelector:
    def __init__(self, locator):
        self.tree = s(locator)
