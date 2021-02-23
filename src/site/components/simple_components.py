import time

import allure
from selene.core import query
from selene.support.conditions import be, have
from selene.support.conditions.be import not_
from selene.support.shared.jquery_style import s, ss


class SearchInput:
    def __init__(self, locator):
        self.input = s(locator)
        self.clear_icon = self.input.s("i.ant-input-clear-icon")

    @allure.step
    def search(self, text: str):
        self.input.set_value(text)
        time.sleep(1)  # TODO workaround, replace with the waiter

    @allure.step
    def clear(self):
        self.clear_icon.click()
        self.input.wait.until(be.empty)

    @allure.step
    def is_empty(self) -> bool:
        return self.input.matching(be.blank)

    @allure.step
    def get_text(self) -> str:
        return self.input.get(query.text)

    @allure.step
    def get_placeholder(self) -> str:
        return self.input.get(query.attribute("placeholder"))


class SelectBox:
    def __init__(self, select_box_locator, items_locator):
        self.select = s(select_box_locator)
        self.items = ss(items_locator)

    @allure.step
    def open(self):
        if not self.is_opened():
            self.select.click()
        return self

    @allure.step
    def is_opened(self) -> bool:
        return self.select.matching(have.css_class("ant-select-open"))

    @allure.step
    def is_empty(self) -> bool:
        return self.select.s(".ant-select-selection-selected-value").matching(not_.present)

    @allure.step
    def select_item(self, item: str):
        self.open()
        self.items.filtered_by(have.text(item))[0].click()
        # self.select_box.s("//li[@role='option'][text()='{}']".format(item)).click()

    @allure.step
    def get_selected_item(self) -> str:
        return self.select.s(".ant-select-selection-selected-value").get(query.text)

    @allure.step
    def get_placeholder(self) -> str:
        return self.select.s(".ant-select-selection__placeholder").get(query.text)

    @allure.step
    def get_label(self) -> str:
        return self.select.s("./ancestor::*[@class='ant-row ant-form-item']//label").get(query.text)

    @allure.step
    def is_enabled(self) -> bool:
        return self.select.matching(be.enabled)


class TreeSelector:
    def __init__(self, tree_selector_locator, child_tree_locator):
        self.tree_selector = s(tree_selector_locator)
        self.selected_items = ss("li.ant-select-selection__choice")
        self.child_tree = _SelectorChildTree(child_tree_locator)

    def open(self):
        self.tree_selector.click()
        return self

    def select_all(self):
        self.open()
        self.child_tree.check()

    # TODO Add all other methods

    @allure.step
    def get_all_selected_items(self) -> []:
        if len(self.selected_items) > 0:
            return self._extract_titles(self.selected_items)
        else:
            return []

    @allure.step
    def get_last_selected_item(self):
        return self.selected_items[-1].get(query.attribute("title"))

    @allure.step
    def remove_selected_item(self, item_name: str):
        self._get_selected_item_element(item_name).s("i.ant-select-remove-icon").click()

    @allure.step
    def _get_selected_item_element(self, item_name: str):
        return self.selected_items.filtered_by(have.attribute("title").value(item_name))

    @staticmethod
    def _extract_titles(elements: []) -> []:
        return [el.get(query.attribute("title")) for el in elements]


class _SelectorChildTree:
    CHECKED_CHECKBOX_CLASS = have.css_class("ant-select-tree-checkbox-checked")

    def __init__(self, locator):
        self.tree = s(locator)
        self.tree_switcher = self.tree.s(".ant-select-tree-switcher")
        self.tree_checkbox = self.tree.s(".ant-select-tree-checkbox")
        self.tree_node = self.tree.s(".ant-select-tree-node-content-wrapper")

    @allure.step
    def is_opened(self) -> bool:
        return self.tree_switcher.matching(have.css_class("ant-select-tree-switcher_open"))

    @allure.step
    def is_closed(self) -> bool:
        return self.tree_switcher.matching(have.css_class("ant-select-tree-switcher_close"))

    @allure.step
    def open(self):
        if self.is_closed():
            self._click_tree_switcher()
        return self

    @allure.step
    def close(self):
        if self.is_opened():
            self._click_tree_switcher()
        return self

    @allure.step
    def is_checked(self) -> bool:
        return self.tree_checkbox.matching(have.css_class(self.CHECKED_CHECKBOX_CLASS))

    @allure.step
    def check(self):
        if not self.is_checked():
            self.tree_checkbox.click().wait.until(have.css_class(self.CHECKED_CHECKBOX_CLASS))
        return self

    @allure.step
    def uncheck(self):
        if self.is_checked():
            self.tree_checkbox.click().wait.until(have.no.css_class(self.CHECKED_CHECKBOX_CLASS))
        return self

    def get_item(self) -> str:
        return self.tree_node.get(query.attribute("title"))

    def _click_tree_switcher(self):
        self.tree_switcher.click()
