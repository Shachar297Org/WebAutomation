import time

import allure
from selene.core import query
from selene.support.conditions import be, have
from selene.support.conditions.be import not_
from selene.support.shared.jquery_style import s, ss

from src.util.elements_util import extract_text


class SearchInput:
    def __init__(self, locator):
        self.input = s(locator)
        self.clear_icon = self.input.s("i.ant-input-clear-icon")

    @allure.step
    def search(self, text: str):
        self.input.set_value(text)
        time.sleep(1)

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
    def __init__(self, select_box_locator):
        self.select = s(select_box_locator)
        self.items = ss(".ant-select-dropdown--single:not(.ant-select-dropdown-hidden) ul li")

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
        self.items.filtered_by(have.exact_text(item)).first.click()

    @allure.step
    def get_items(self) -> []:
        self.open()
        return list(filter(None, extract_text(ss(".ant-select-dropdown ul li"))))

    @allure.step
    def get_selected_item(self) -> str:
        if self.is_empty():
            return ""
        else:
            return self.select.s(".ant-select-selection-selected-value").get(query.text)

    @allure.step
    def get_placeholder(self) -> str:
        return self.select.s(".ant-select-selection__placeholder").get(query.text)

    @allure.step
    def get_label(self) -> str:
        return self.select.s("./ancestor::*[@class='ant-row ant-form-item']//label").get(query.text)

    @allure.step
    def wait_to_be_enabled(self):
        self.select.wait.until(have.css_class("ant-select-enabled"))
        return self

    @allure.step
    def wait_to_be_not_empty(self):
        self.wait_to_be_enabled()
        self.items.wait.until(have.size_greater_than_or_equal(1))
        return self

    @allure.step
    def is_enabled(self) -> bool:
        return self.select.matching(have.css_class("ant-select-enabled"))

    @allure.step
    def is_disabled(self) -> bool:
        return self.select.matching(have.css_class("ant-select-disabled"))


class Tooltip:
    _TOOLTIP_LOCATOR = ".ant-tooltip:not(.ant-tooltip-hidden)"

    def __init__(self):
        self.tooltip = s(self._TOOLTIP_LOCATOR)

    @allure.step
    def wait_to_be_loaded(self):
        time.sleep(3)  # TODO replaces with waiter
        self.tooltip.wait.until(be.visible)
        return self

    @allure.step
    def is_displayed(self) -> bool:
        return self.tooltip.matching(be.present)

    @allure.step
    def get_items(self) -> []:
        return self.tooltip.ss("li span")

    @allure.step
    def get_items_text(self) -> []:
        return extract_text(self.get_items())


class TopRightNotification:
    def __init__(self):
        self.notification = s(".ant-notification-topRight")
        self.message = self.notification.s(".ant-notification-notice-message")
        self.description = self.notification.s(".ant-notification-notice-description")
        self.close_button = self.notification.s(".ant-notification-close-icon")

    @allure.step
    def wait_to_load(self):
        self.message.wait.until(be.visible)

    @allure.step
    def get_message(self) -> str:
        self.wait_to_load()
        return self.message.get(query.text)

    @allure.step
    def get_description(self) -> str:
        self.wait_to_load()
        return self.description.get(query.text)

    @allure.step
    def close(self):
        self.wait_to_load()
        self.close_button.click()
        self.message.wait.until(be.not_.visible)

    def should_be_visible(self):
        self.notification.should(be.visible)

    def should_not_be_visible(self):
        self.notification.should(be.not_.visible)