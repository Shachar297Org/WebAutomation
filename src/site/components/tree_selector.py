import allure
from selene.core import query, command
from selene.core.entity import Element
from selene.support.conditions import have
from selene.support.shared.jquery_style import s, ss

from src.util.elements_util import extract_text

ALL_NODE = "ALL"
_SELECT_TREE_LOCATOR = ".tree-selector-drop-down:not(.ant-select-dropdown-hidden)"


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

    def _click_tree_switcher(self):
        self.switcher.perform(command.js.scroll_into_view()).click()

    def _click_checkbox(self) -> Element:
        return self.tree_checkbox.perform(command.js.scroll_into_view()).click()


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
        self.selected_items = ss("li.ant-select-selection__choice")

        self.select_tree = s(_SELECT_TREE_LOCATOR)

    def open(self):
        self.tree_selector.click()
        return self

    @allure.step
    def get_all_selected_items(self) -> []:
        if len(self.selected_items) > 0:
            return self._extract_titles(self.selected_items)
        else:
            return []

    @allure.step
    def get_last_selected_item(self) -> str:
        return self.selected_items[-1].get(query.attribute("title"))

    @allure.step
    def remove_selected_item(self, item_name: str):
        self._get_selected_item_element(item_name).s("i.ant-select-remove-icon").click()
        return self

    @allure.step
    def is_enabled(self) -> bool:
        return self.tree_selector.matching(have.css_class("ant-select-enabled"))

    @allure.step
    def _get_selected_item_element(self, item_name: str):
        return self.selected_items.filtered_by(have.attribute("title").value(item_name))

    @staticmethod
    def _extract_titles(elements: []) -> []:
        return [el.get(query.attribute("title")) for el in elements]


class DeviceLocationTreeSelector(_BaseTreeSelector):
    def __init__(self, tree_selector_locator):
        super().__init__(tree_selector_locator)
        self.all_tree = _ChildTree("ul")
        self.region_tree = _ChildTree("ul ul")
        self.country_tree = _ChildTree("ul ul ul")

    @allure.step
    def select_all(self):
        self.open()
        self.all_tree.get_node_by_name(ALL_NODE).check()

    @allure.step
    def deselect_all(self):
        self.open()
        self.all_tree.get_node_by_name(ALL_NODE).uncheck()

    @allure.step
    def select_region(self, text):
        self.open()
        self.region_tree.get_node_by_name(text).check()

    @allure.step
    def select_country(self, text):
        self.open()
        self.country_tree.get_node_by_name(text).check()


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

    # TODO add all needed methods
