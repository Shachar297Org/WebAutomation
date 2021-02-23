import time

import allure
from selene.core import query
from selene.core.entity import Element
from selene.support.conditions import be, have
from selene.support.shared.jquery_style import s


class _BaseTable(object):
    _HEADER_XPATH = ".//th//span[@class='ant-table-column-title']"

    def __init__(self, locator: str):
        self.table = s(locator)
        self.table_body = self.table.s("tbody.ant-table-tbody")
        self.rows = self.table_body.ss("tr")

    def wait_to_load(self):
        self.table_body.wait.until(be.visible)
        return self

    @allure.step
    def get_headers(self) -> []:
        headers = self.table.ss(self._HEADER_XPATH)
        return _BaseTable._extract_text(headers)

    @allure.step
    def get_column_values(self, column_name: str, ) -> []:
        self.wait_to_load()
        cells = self.table.ss(".//tbody/tr/td[{0}]".format(self._get_column_index(column_name)))
        return _BaseTable._extract_text(cells)

    @allure.step
    def get_row_by_column_value(self, column_name: str, column_value: str) -> Element:
        self.wait_to_load()
        return self.table.s(".//tbody/tr[td[{0}][text()='{1}']]"
                            .format(self._get_column_index(column_name), column_value))

    @allure.step
    def get_rows_by_column_value(self, column_name: str, column_value: str) -> []:
        self.wait_to_load()
        return self.table.ss(".//tbody/tr[td[{0}][text()='{1}']]"
                             .format(self._get_column_index(column_name), column_value))

    @allure.step("Get table row by source column value and return the target column value")
    def get_column_value(self, src_column_name: str, src_column_value: str,
                         target_column: str) -> str:
        self.wait_to_load()
        target_column_index = self._get_column_index(target_column)
        return self.get_row_by_column_value(src_column_name, src_column_value) \
            .s("./td[{0}]".format(target_column_index)).get(query.text)

    @allure.step("Sort table rows by column value in Ascending (A to Z) order")
    def sort_asc(self, column_name):
        icon = self._get_column_sort_icon_up(column_name)
        self._click_sort_icon(icon)
        icon.wait.until(have.css_class("on"))

    @allure.step("Sort table rows by column value in Descending (Z to A) order")
    def sort_desc(self, column_name):
        icon = self._get_column_sort_icon_down(column_name)
        self._click_sort_icon(icon)
        icon.wait.until(have.css_class("on"))

    @allure.step
    def is_column_sorted(self, column_name) -> bool:
        return self.is_up_icon_blue(column_name) or self.is_up_icon_blue(column_name)

    @allure.step("Check whether sorting blue icon up is displayed for the column header")
    def is_up_icon_blue(self, column_name) -> bool:
        return self._get_column_sort_icon_up(column_name).matching(have.css_class("on"))

    @allure.step("Check whether sorting blue icon down is displayed for the column header")
    def is_down_icon_blue(self, column_name) -> bool:
        return self._get_column_sort_icon_down(column_name).matching(have.css_class("on"))

    @allure.step
    def is_any_row_cell_contains_text_ignoring_case(self, table_row: Element, text: str) -> bool:
        for cell_text in self._extract_text(self._get_raw_cells(table_row)):
            if text.lower() in cell_text.lower():
                return True

    def _get_header(self, header_name) -> Element:
        return self.table.s(self._HEADER_XPATH + "[text()='{}']".format(header_name))

    def _get_column_sorter(self, header_name) -> Element:
        return self.table.s(".//th//*[@class='ant-table-column-sorters'][./span[text()='{}']]".format(header_name))

    def _get_column_index(self, column_name: str) -> int:
        return len(self.table.ss(".//th[.//span[@class='ant-table-column-title'][text()='{}']]/preceding-sibling::*"
                                 .format(column_name))) + 1

    def _get_column_sort_icon_up(self, header_name) -> Element:
        return self._get_column_sorter(header_name).s("i.ant-table-column-sorter-up")

    def _get_column_sort_icon_down(self, header_name) -> Element:
        return self._get_column_sorter(header_name).s("i.ant-table-column-sorter-down")

    @allure.step
    def _get_row_button_by_column_value(self, column_name: str, column_value: str) -> Element:
        return self.get_row_by_column_value(column_name, column_value).s("button")

    @allure.step
    def _get_row_button_with_name_by_column_value(self, column_name: str, column_value: str,
                                                  button_name: str) -> Element:
        return self.get_row_by_column_value(column_name, column_value) \
            .s("./button[span[text()='{}']]".format(button_name))

    @staticmethod
    def get_row_cell_text_by_index(row: Element, index: int) -> str:
        return row.s("./td[{0}]".format(index)).get(query.text)

    @staticmethod
    def _click_sort_icon(icon: Element):
        icon.s("svg").click()
        time.sleep(1)

    @staticmethod
    def _get_raw_cells(table_row: Element) -> []:
        return table_row.ss("td")

    @staticmethod
    def _extract_text(elements: []) -> []:
        return [el.get(query.text) for el in elements]


class PaginationElement(object):
    def __init__(self, locator: str):
        self.pagination_element = s(locator)
        self.counter = s("li.ant-pagination-item a")
        self.left_arrow = s("i.anticon-left")
        self.left_right = s("i.anticon-right")

    def get_counter(self) -> int:
        return int(self.pagination_element.get(query.text))
