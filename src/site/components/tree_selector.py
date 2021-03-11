import time

import allure
from selene.core import query, command
from selene.core.entity import Element
from selene.support.conditions import have, be
from selene.support.shared.jquery_style import s

from src.util.elements_util import extract_text, extract_titles

SEPARATOR = "/"
ALL_NODE = "ALL"
_SELECT_TREE_LOCATOR = ".tree-selector-drop-down:not(.ant-select-dropdown-hidden)"


def get_formatted_selected_plus_item(number) -> str:
    return "+ {} ...".format(number)


class _TreeNodeWrapper:
    CHECKED_CHECKBOX_CLASS = have.css_class("ant-select-tree-checkbox-checked")

    def __init__(self, tree_node_element: Element):
        self._tree_node = tree_node_element
        self.switcher = self._tree_node.s(".ant-select-tree-switcher")
        self.tree_checkbox = self._tree_node.s(".ant-select-tree-checkbox")
        self.content = self._tree_node.s(".ant-select-tree-node-content-wrapper")

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
            self._click_checkbox().wait.until(have.css_class(self.CHECKED_CHECKBOX_CLASS))
        return self

    @allure.step
    def uncheck(self):
        if self.is_checked():
            self._click_checkbox().wait.until(have.no.css_class(self.CHECKED_CHECKBOX_CLASS))
        return self

    def get_item(self) -> str:
        return self.content.get(query.attribute("title"))

    def _click_tree_switcher(self) -> Element:
        self.switcher.perform(command.js.scroll_into_view)
        return self.switcher.click()

    def _click_checkbox(self) -> Element:
        self.tree_checkbox.perform(command.js.scroll_into_view)
        return self.tree_checkbox.click()


class _ChildTree:
    def __init__(self, locator):
        self.tree = s(_SELECT_TREE_LOCATOR).s(locator)

    @allure.step
    def get_node_by_name(self, name) -> _TreeNodeWrapper:
        return _TreeNodeWrapper(self.tree.s("./li/span[@title='{}']/parent::li".format(name)))

    @allure.step
    def get_nodes(self) -> []:
        return self.tree.ss("./li")

    @allure.step
    def get_node_names(self) -> []:
        return extract_text(self.tree.ss("./li/span[@title]"))


class _BaseTreeSelector:
    def __init__(self, tree_selector_locator):
        self.tree_selector = s(tree_selector_locator)
        self.search_input = self.tree_selector.s("input.ant-select-search__field")
        self.selected_items = self.tree_selector.ss("li.ant-select-selection__choice")

        self.select_tree = s(_SELECT_TREE_LOCATOR)

    @allure.step
    def open(self):
        if not self.is_opened():
            is_another_tree_selector_open = self._is_another_tree_selector_is_opened()
            self.tree_selector.click()
            if is_another_tree_selector_open:
                time.sleep(1)
        return self

    @allure.step
    def is_opened(self) -> bool:
        return self.tree_selector.matching(have.css_class("ant-select-open"))

    @allure.step
    def filter(self, text):
        self.search_input.set_value(text)
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
    def _get_selected_item_element(self, item_name: str):
        return self.selected_items.filtered_by(have.attribute("title").value(item_name)).first

    def _is_another_tree_selector_is_opened(self) -> bool:
        return self.tree_selector.matching(be.present)


class DeviceLocationTreeSelector(_BaseTreeSelector):
    def __init__(self, tree_selector_locator):
        super().__init__(tree_selector_locator)
        self.all_tree = _ChildTree("ul")
        self.region_tree = _ChildTree("ul ul")
        self.country_tree = _ChildTree("ul ul ul")
        self.state_tree = _ChildTree("ul ul ul ul")

    @allure.step
    def select_all(self):
        self.open()
        self._get_all_node().check()

    @allure.step
    def deselect_all(self):
        self.open()
        self._get_all_node().uncheck()

    @allure.step
    def select_regions(self, *regions):
        self.open()
        self._get_all_node().open()

        for region in regions:
            self._check_region(region)

    @allure.step
    def select_countries(self, region, *countries):
        self.open()
        self._get_all_node().open()
        self._open_region(region)

        for country in countries:
            self._check_country(country)

    @allure.step
    def select_usa_states(self, *states):
        self.open()
        self._get_all_node().open()
        self._open_region("Americas")
        self._open_country("USA")

        for state in states:
            self._check_state(state)

    @allure.step
    def _get_all_node(self):
        return self.all_tree.get_node_by_name(ALL_NODE)

    @allure.step
    def _check_region(self, text):
        self.region_tree.get_node_by_name(text).check()

    @allure.step
    def _open_region(self, text):
        self.region_tree.get_node_by_name(text).open()

    @allure.step
    def _check_country(self, text):
        self.country_tree.get_node_by_name(text).check()

    @allure.step
    def _open_country(self, text):
        self.country_tree.get_node_by_name(text).open()

    @allure.step
    def _check_state(self, text):
        self.state_tree.get_node_by_name(text).check()


class DeviceTypesTreeSelector(_BaseTreeSelector):
    def __init__(self, tree_selector_locator):
        super().__init__(tree_selector_locator)
        self.all_tree = _ChildTree("ul")
        self.device_type_tree = _ChildTree("ul ul")
        self.device_model_tree = _ChildTree("ul ul ul")
        self.device_tree = _ChildTree("ul ul ul ul")

    @allure.step
    def select_all(self):
        self.open()
        self.all_tree.get_node_by_name(ALL_NODE).check()

    @allure.step
    def deselect_all(self):
        self.open()
        self.all_tree.get_node_by_name(ALL_NODE).uncheck()

    @allure.step
    def select_device_types(self, *device_types):
        self.open()
        self._get_all_node().open()

        for dev_type in device_types:
            self._check_device_type(dev_type)

    @allure.step
    def get_all_device_types(self) -> []:
        self.open()
        self._get_all_node().open()

        return self.device_type_tree.get_node_names()

    @allure.step
    def select_device_model(self, device_type, *device_models):
        self.open()
        self._get_all_node().open()
        self._open_device_type(device_type)

        for model in device_models:
            self._check_device_model(model)

    @allure.step
    def select_devices(self, device_type, device_model, *devices):
        self.open()
        self._get_all_node().open()
        self._open_device_type(device_type)
        self._open_device_model(device_model)

        for device in devices:
            self._check_device(device)

    @allure.step
    def _get_all_node(self):
        return self.all_tree.get_node_by_name(ALL_NODE)

    @allure.step
    def _check_device_type(self, text):
        self.device_type_tree.get_node_by_name(text).check()

    @allure.step
    def _open_device_type(self, text):
        self.device_type_tree.get_node_by_name(text).open()

    @allure.step
    def _check_device_model(self, text):
        self.device_model_tree.get_node_by_name(text).check()

    @allure.step
    def _open_device_model(self, text):
        self.device_model_tree.get_node_by_name(text).open()

    @allure.step
    def _check_device(self, text):
        self.device_tree.get_node_by_name(text).check()
