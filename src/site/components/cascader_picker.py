import time

import allure
from selene.core import query, command
from selene.core.entity import Element
from selene.support.conditions import have
from selene.support.shared.jquery_style import s

from src.util.elements_util import extract_titles


SEPARATOR = "/"


class _BaseCascaderPicker:

    def __init__(self, picker_locator):
        self.picker = s(picker_locator)
        self.input = self.picker.s("input.ant-cascader-input")
        self.selected_item = self.picker.s(".ant-cascader-picker-label")
        self.clear_button = self.picker.s(".ant-cascader-picker-clear")
        self.cascader_menu = s("div.ant-cascader-menus:not(.ant-cascader-menus-hidden)")
        self.filtered_items = self.cascader_menu.ss("li.ant-cascader-menu-item")
        self.selected_menu_items = self.cascader_menu.ss("li.ant-cascader-menu-item-active")

        self.first_menu = self.cascader_menu.s(".//ul[1]")
        self.second_menu = self.cascader_menu.s(".//ul[2]")
        self.third_menu = self.cascader_menu.s(".//ul[3]")

    @allure.step
    def open(self):
        if not self.is_opened():
            self.picker.click()
            time.sleep(1)
        return self

    @allure.step
    def is_opened(self) -> bool:
        return self.picker.matching(have.css_class("ant-cascader-picker-focused"))

    @allure.step
    def is_disabled(self) -> bool:
        return self.input.matching(have.css_class("ant-input-disabled"))

    @allure.step
    def select_item_by_keyword(self, keyword: str):
        self.filter(keyword)
        self.filtered_items.filtered_by(have.text(keyword)).first.click()

    @allure.step
    def _expand_first_level_item(self, text) -> Element:
        self.open()
        return self._expand_menu_item(self.first_menu, text)

    @allure.step
    def _expand_second_level_item(self, first_level_item: str, second_level_item: str) -> Element:
        second_level_menu = self._expand_first_level_item(first_level_item)
        return self._expand_menu_item(second_level_menu, second_level_item)

    @allure.step
    def _select_second_level_item(self, first_level_item: str, second_level_item: str) -> Element:
        second_level_menu = self._expand_first_level_item(first_level_item)
        return self._select_menu_item(second_level_menu, second_level_item)

    @allure.step
    def _select_third_level_item(self, first_level_item: str, second_level_item: str,
                                 third_level_item: str) -> Element:
        third_level_menu = self._expand_second_level_item(first_level_item, second_level_item)
        return self._select_menu_item(third_level_menu, third_level_item)

    @allure.step
    def filter(self, text):
        self.input.set_value(text).press_enter()
        return self

    @allure.step
    def get_selected_item(self) -> str:
        return self.selected_item.get(query.text)

    @allure.step
    def get_selected_menu_items(self) -> []:
        if len(self.selected_menu_items) > 0:
            return extract_titles(self.selected_menu_items)
        else:
            return []

    @allure.step
    def clear(self):
        self.input.hover()
        time.sleep(1)
        self.clear_button.click()
        return self

    @allure.step
    def _expand_menu_item(self, menu: Element, text: str) -> Element:
        self._select_menu_item(menu, text)
        return menu.s("./following-sibling::ul")

    @allure.step
    def _select_menu_item(self, menu: Element, text: str):
        menu.s("./li[@title='{}']".format(text)).perform(command.js.scroll_into_view).click()


class DeviceTypeCascaderPicker(_BaseCascaderPicker):

    @allure.step
    def select_device(self, group: str, model: str, device: str):
        self._select_third_level_item(group, model, device)
        return self


class RegionCountryCascaderPicker(_BaseCascaderPicker):

    @allure.step
    def filter(self, text):
        self.input.click().set_value(text)
        return self

    @allure.step
    def select_country(self, region: str, country: str):
        self._select_second_level_item(region, country)
