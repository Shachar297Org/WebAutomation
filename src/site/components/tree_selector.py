import time

import allure
from selene.core import query, command
from selene.core.entity import Element
from selene.support.conditions import have, be
from selene.support.shared.jquery_style import s

from src.const import AmericasCountry, Region
from src.util.elements_util import extract_text, extract_titles

SEPARATOR = "/"
ALL_NODE = "ALL"


def get_formatted_selected_plus_item(number) -> str:
    return "+ {} ...".format(number)


class _TreeNodeWrapper:
    _CHECKED_CHECKBOX_CLASS = "ant-select-tree-checkbox-checked"

    def __init__(self, tree_node_element: Element):
        self._node = tree_node_element

        self.switcher = self._node.s(".ant-select-tree-switcher")
        self.tree_checkbox = self._node.s(".ant-select-tree-checkbox")
        self.content = self._node.s(".ant-select-tree-node-content-wrapper")

    @allure.step
    def is_opened(self) -> bool:
        return self.switcher.matching(have.css_class("ant-select-tree-switcher_open"))

    @allure.step
    def is_closed(self) -> bool:
        return self.switcher.matching(have.css_class("ant-select-tree-switcher_close"))

    @allure.step
    def has_child(self) -> bool:
        return self.switcher.matching(have.no.css_class("ant-select-tree-switcher-noop"))

    @allure.step
    def open(self):
        if self.is_closed():
            self._click_tree_switcher()
        return _ChildTreeWrapper(self._node.s("ul.ant-select-tree-child-tree"))

    @allure.step
    def close(self):
        if self.is_opened():
            self._click_tree_switcher()
        return self

    @allure.step
    def is_checked(self) -> bool:
        return self.tree_checkbox.matching(have.css_class(self._CHECKED_CHECKBOX_CLASS))

    @allure.step
    def check(self):
        if not self.is_checked():
            self._click_checkbox().wait.until(have.css_class(self._CHECKED_CHECKBOX_CLASS))
        return self

    @allure.step
    def uncheck(self):
        if self.is_checked():
            self._click_checkbox().wait.until(have.no.css_class(self._CHECKED_CHECKBOX_CLASS))
        return self

    @allure.step
    def get_title(self) -> str:
        return self.content.get(query.attribute("title"))

    def _click_tree_switcher(self) -> Element:
        self.switcher.perform(command.js.scroll_into_view)
        return self.switcher.click()

    def _click_checkbox(self) -> Element:
        self.tree_checkbox.perform(command.js.scroll_into_view)
        return self.tree_checkbox.click()


class _ChildTreeWrapper:
    def __init__(self, tree_element: Element):
        self.tree = tree_element

    @allure.step
    def get_node_by_name(self, name) -> _TreeNodeWrapper:
        return _TreeNodeWrapper(self.tree.s("./li/span[@title='{}']/parent::li".format(name)))

    @allure.step
    def get_nodes(self) -> []:
        return self.tree.ss("./li")

    @allure.step
    def get_node_titles(self) -> []:
        return extract_text(self.tree.ss("./li/span[@title]"))


class TreeSelector:
    def __init__(self, tree_selector_locator: str):
        self.tree_selector = s(tree_selector_locator)

        self.search_input = self.tree_selector.s("input.ant-select-search__field")
        self.dropdown_search_input = s(".ant-select-dropdown input.ant-select-search__field")
        self.selected_items = self.tree_selector.ss("li.ant-select-selection__choice")
        self.placeholder = self.tree_selector.s(".ant-select-search__field__placeholder")
        self.clear_button = self.tree_selector.s("i.ant-select-clear-icon")
        self.select_tree = s(".tree-selector-drop-down:not(.ant-select-dropdown-hidden)")

    @allure.step
    def open(self):
        if not self.is_opened():
            is_another_tree_selector_open = self._is_another_tree_selector_opened()
            self.tree_selector.click()
            if is_another_tree_selector_open:
                time.sleep(1)
        return self

    @allure.step
    def close(self):
        self.tree_selector.press_escape()
        self.tree_selector.should(have.no.css_class("ant-select-open"))

    @allure.step
    def is_opened(self) -> bool:
        return self.tree_selector.matching(have.css_class("ant-select-open"))

    @allure.step
    def search(self, text):
        self.search_input.set_value(text)
        return self

    @allure.step
    def dropdown_search(self, text):
        self.dropdown_search_input.set_value(text)
        return self

    @allure.step
    def get_all_selected_items(self) -> []:
        if len(self.selected_items) > 0:
            return extract_titles(self.selected_items)
        else:
            return []

    @allure.step
    def get_last_selected_item(self) -> str:
        return self.selected_items[-1].get(query.attribute("title"))

    @allure.step
    def remove_selected_item(self, item_name: str):
        existing_items_count = len(self.selected_items)
        self._get_selected_item_element(item_name).s("i.ant-select-remove-icon").click()
        self.selected_items.wait_until(have.size_less_than(existing_items_count))
        return self

    @allure.step
    def is_enabled(self) -> bool:
        return self.tree_selector.matching(have.css_class("ant-select-enabled"))

    @allure.step
    def is_disabled(self) -> bool:
        return self.tree_selector.matching(have.css_class("ant-select-disabled"))

    @allure.step
    def get_placeholder(self) -> str:
        return self.placeholder.get(query.text)

    @allure.step
    def select_all(self):
        self.open()
        self._get_node_by_title(ALL_NODE).check()
        return self

    @allure.step
    def deselect_all(self):
        self.open()
        self._get_node_by_title(ALL_NODE).uncheck()

    @allure.step
    def select_filtered_item(self, item: str):
        s(".//span[@class='ant-select-tree-title'][text()='" + item + "']").click()

    @allure.step
    def _select_first_level_items(self, *titles):
        self.open()
        for title in titles:
            self._get_node_by_title(title).check()

    @allure.step
    def _select_second_level_items(self, first_level_title: str, *second_level_titles):
        self.open()
        tree = self._open_first_level_tree(first_level_title)
        for title in second_level_titles:

            tree.get_node_by_name(title).check()

    @allure.step
    def _select_third_level_items(self, first_level_title: str, second_level_title: str, *third_level_titles):
        self.open()
        tree = self._open_second_level_tree(first_level_title, second_level_title)
        for title in third_level_titles:
            tree.get_node_by_name(title).check()

    @allure.step
    def _open_first_level_tree(self, title: str) -> _ChildTreeWrapper:
        return self._get_node_by_title(title).open()

    @allure.step
    def _open_second_level_tree(self, first_level_title: str, second_level_title: str) -> _ChildTreeWrapper:
        tree = self._open_first_level_tree(first_level_title)
        return tree.get_node_by_name(second_level_title).open()

    @allure.step
    def _open_third_level_tree(self, first_level_title: str, second_level_title: str,
                               third_level_title: str) -> _ChildTreeWrapper:
        tree = self._open_second_level_tree(first_level_title, second_level_title)
        return tree.get_node_by_name(third_level_title).open()

    @allure.step
    def _get_node_by_title(self, title: str) -> _TreeNodeWrapper:
        return _TreeNodeWrapper(self.select_tree.s(".//li[@role='treeitem'][./*[@title='{}']]".format(title)))

    def _get_selected_item_element(self, item_name: str):
        return self.selected_items.filtered_by(have.attribute("title").value(item_name)).first

    def _is_another_tree_selector_opened(self) -> bool:
        return self.tree_selector.matching(be.present)


class LocationTreeSelector(TreeSelector):

    @allure.step
    def select_regions(self, *regions):
        self._select_first_level_items(*regions)
        return self

    @allure.step
    def select_countries(self, region, *countries):
        self._select_second_level_items(region, *countries)
        return self

    @allure.step
    def select_usa_states(self, *states):
        self._select_third_level_items(Region.AMERICAS, AmericasCountry.USA, *states)
        return self


class DeviceTypesTreeSelector(TreeSelector):

    @allure.step
    def select_device_groups(self, *device_groups):
        self._select_first_level_items(*device_groups)
        return self

    @allure.step
    def select_device_models(self, device_group, *device_models):
        self._select_second_level_items(device_group, *device_models)
        return self

    @allure.step
    def select_devices(self, device_group, device_model, *devices):
        self._select_third_level_items(device_group, device_model, *devices)
        return self

