import allure
from selene.core import query
from selene.core.entity import Element
from selene.support.conditions import be, have
from selene.support.shared.jquery_style import s

from src.site.components.simple_components import Tooltip
from src.util.elements_util import extract_text


class TableRowWrapper:
    def __init__(self, table_row_element: Element):
        self.row = table_row_element
        self._table = self.row.s("./ancestor::*[starts-with(@class, 'ant-table-wrapper')]")
        self.cells = self.row.ss("td")
        self.button = self.row.s("button")

    @allure.step
    def get_cell(self, column_name: str) -> Element:
        return self._get_cell_by_index(self._get_column_index(column_name))

    @allure.step
    def get_cell_text(self, column_name: str) -> str:
        return self.get_cell(column_name).get(query.text)

    @allure.step
    def hover_column_cell(self, column_name: str) -> Tooltip:
        self.get_cell(column_name).hover()
        return Tooltip()

    @allure.step
    def has_button_with_text(self, button_name: str) -> bool:
        return self.row.s(".//button[span[text()='{}']]".format(button_name)).matching(be.visible)

    @allure.step
    def click_button(self, button_text: str):
        self.get_button(button_text).click()

    @allure.step
    def get_button(self, button_text: str) -> Element:
        return self.row.s(".//button[span[text()='{}']]".format(button_text))

    @allure.step
    def is_selected(self) -> bool:
        return self.row.matching(have.css_class("selected"))

    def _get_cell_by_index(self, column_index) -> Element:
        return self.row.s("./td[{}]".format(column_index))

    def _get_column_index(self, column_name: str) -> int:
        return len(self._table.ss(".//th[.//span[@class='ant-table-column-title'][text()='{}']]/preceding-sibling::*"
                                  .format(column_name))) + 1


class _BaseTable(object):
    _ROW_BY_COLUMN_VALUE_XPATH = ".//tbody/tr[td[{0}][./descendant-or-self::text()='{1}']]"

    def __init__(self, locator: str):
        self.table = s(locator)
        self.table_body = self.table.s("tbody.ant-table-tbody")
        self.spinner = s('.ant-spin-blur')

    @allure.step
    def wait_to_load(self):
        self.table_body.wait.until(be.visible)
        self.spinner.wait.until(be.not_.visible)
        return self

    @allure.step
    def get_rows(self):
        return self._get_wrapped_rows(self.table_body.ss("tr"))

    @allure.step
    def get_headers(self) -> []:
        headers = self.table.ss(".//th//span[@class='ant-table-column-title']")
        return extract_text(headers)

    @allure.step
    def get_column_values(self, column_name: str) -> []:
        self.wait_to_load()
        cells = self.table.ss(".//tbody/tr/td[{}]".format(self._get_column_index(column_name)))
        return extract_text(cells)

    @allure.step
    def get_row_by_column_value(self, column_name: str, column_value: str) -> TableRowWrapper:
        self.wait_to_load()
        return TableRowWrapper(self.table.s(self._ROW_BY_COLUMN_VALUE_XPATH.format(
            self._get_column_index(column_name), column_value)))

    @allure.step
    def get_rows_by_column_value(self, column_name: str, column_value: str) -> []:
        self.wait_to_load()
        row_elements = self.table.ss(self._ROW_BY_COLUMN_VALUE_XPATH.format(
            self._get_column_index(column_name), column_value))
        return self._get_wrapped_rows(row_elements)

    @allure.step("Sort table rows by column value in Ascending (A to Z) order")
    def sort_asc(self, column_name):
        self._sort(self._get_column_sort_icon_up(column_name))

    @allure.step("Sort table rows by column value in Descending (Z to A) order")
    def sort_desc(self, column_name):
        self._sort(self._get_column_sort_icon_down(column_name))

    @allure.step
    def is_column_sorted(self, column_name) -> bool:
        return self.is_up_icon_blue(column_name) or self.is_down_icon_blue(column_name)

    @allure.step("Check whether sorting blue icon up is displayed for the column header")
    def is_up_icon_blue(self, column_name) -> bool:
        return self._get_column_sort_icon_up(column_name).matching(have.css_class("on"))

    @allure.step("Check whether sorting blue icon down is displayed for the column header")
    def is_down_icon_blue(self, column_name) -> bool:
        return self._get_column_sort_icon_down(column_name).matching(have.css_class("on"))

    @allure.step
    def is_any_row_cell_contains_text_ignoring_case(self, table_row: TableRowWrapper, text: str) -> bool:
        for cell_text in extract_text(table_row.cells):
            if text.lower() in cell_text.lower():
                return True

    def _get_column_index(self, column_name: str) -> int:
        return len(self.table.ss(".//th[.//span[@class='ant-table-column-title'][text()='{}']]/preceding-sibling::*"
                                 .format(column_name))) + 1

    def _get_column_sort_icon_up(self, header_name) -> Element:
        return self._get_column_sorter(header_name).s("i.ant-table-column-sorter-up")

    def _get_column_sort_icon_down(self, header_name) -> Element:
        return self._get_column_sorter(header_name).s("i.ant-table-column-sorter-down")

    def _get_column_sorter(self, header_name) -> Element:
        return self.table.s(".//th//*[@class='ant-table-column-sorters'][./span[text()='{}']]".format(header_name))

    def _sort(self, icon):
        for i in range(2):
            if icon.matching(have.css_class("off")):
                icon.s("svg").click()
                self.wait_to_load()

    @staticmethod
    def _get_wrapped_rows(row_elements: []):
        wrapped_rows = []
        for row_el in row_elements:
            wrapped_rows.append(TableRowWrapper(row_el))
        return wrapped_rows


class PaginationElement(object):
    _DISABLED_ARROW_CLASS = "ant-pagination-disabled"

    def __init__(self, locator: str):
        self.element = s(locator)
        self.pagination_active_item = self.element.s("li.ant-pagination-item-active a")
        self.pagination_items = self.element.ss("li.ant-pagination-item a")
        self.left_arrow = self.element.s("li.ant-pagination-prev")
        self.right_arrow = self.element.s("li.ant-pagination-next")

    @allure.step
    def get_active_item_number(self) -> int:
        return int(self.pagination_active_item.get(query.text))

    @allure.step
    def get_all_page_numbers(self) -> []:
        return extract_text(self.pagination_items)

    @allure.step
    def open_page(self, number: int):
        self.element.s(".//li[@title='{}']".format(number))
        return self

    @allure.step
    def is_left_arrow_disabled(self) -> bool:
        return self.left_arrow.matching(have.css_class(self._DISABLED_ARROW_CLASS))

    @allure.step
    def is_right_arrow_disabled(self) -> bool:
        return self.right_arrow.matching(have.css_class(self._DISABLED_ARROW_CLASS))
