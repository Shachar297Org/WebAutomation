import allure
import pytest
from assertpy import assert_that
from selene.support.conditions import be

from src.const import Feature
from src.site.login_page import LoginPage
from src.site.components.tables import DevicesTable
from src.site.pages import DevicesPage
from src.util.random_util import random_list_item
from test.test_data_provider import super_admin_credentials


@pytest.fixture(scope="class")
def login(request):
    home_page = LoginPage().open().login_as(super_admin_credentials)
    if request.cls is not None:
        request.cls.home_page = home_page
    yield home_page


@pytest.mark.usefixtures("login")
@allure.feature(Feature.DEVICES)
class TestDevicesList:
    table_columns_provider = [
        DevicesTable.Headers.SERIAL_NUMBER,
        DevicesTable.Headers.DEVICE_TYPE,
        DevicesTable.Headers.STATUS,
        DevicesTable.Headers.CLINIC_ID,
        DevicesTable.Headers.CLINIC_NAME,
        DevicesTable.Headers.COUNTRY
    ]

    search_columns_provider = [
        DevicesTable.Headers.SERIAL_NUMBER,
        DevicesTable.Headers.STATUS,
        DevicesTable.Headers.CLINIC_ID,
        DevicesTable.Headers.CLINIC_NAME,
        DevicesTable.Headers.COUNTRY
    ]

    @allure.title("Verify Devices page web elements")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_device_page_elements(self):
        devices_page = self.home_page.left_panel.open_devices()
        headers = DevicesTable.Headers

        devices_page.add_button.should(be.visible).should(be.clickable)

        devices_page.search_input.input.should(be.visible).should(be.enabled).should(be.blank)
        assert_that(devices_page.search_input.get_placeholder()).is_equal_to(devices_page.SEARCH_TEXT)

        devices_page.device_tree_picker.tree_selector.should(be.visible)
        assert_that(devices_page.device_tree_picker.is_enabled()) \
            .described_as("'Device Types' tree picker to be enabled").is_true()
        assert_that(devices_page.device_tree_picker.selected_items()) \
            .described_as("'Device Types' tree picker to be empty").is_empty()
        assert_that(devices_page.device_tree_picker.get_placeholder()) \
            .is_equal_to(DevicesPage.DEVICE_TYPES_TEXT)

        devices_page.location_tree_picker.tree_selector.should(be.visible)
        assert_that(devices_page.location_tree_picker.is_enabled()) \
            .described_as("'Location' tree picker to be enabled").is_true()
        assert_that(devices_page.location_tree_picker.selected_items()) \
            .described_as("'Location' tree picker to be empty").is_empty()
        assert_that(devices_page.location_tree_picker.get_placeholder()) \
            .is_equal_to(DevicesPage.LOCATIONS_TEXT)

        devices_page.reset_button.should(be.visible).should(be.clickable)
        devices_page.reload_button.should(be.visible).should(be.clickable)

        devices_page.table.table.should(be.visible).should(be.enabled)
        assert_that(devices_page.table.get_headers()).contains_only(headers.SERIAL_NUMBER, headers.DEVICE_TYPE,
                                                                    headers.STATUS, headers.CLINIC_ID,
                                                                    headers.CLINIC_NAME, headers.COUNTRY,
                                                                    headers.ACTION_BUTTON)

    @allure.title("3.4.1 Verify that you can sort device rows by any column")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.issue("wrong device type sorting order")
    @pytest.mark.parametrize("column", table_columns_provider)
    def test_sort_devices(self, column):
        devices_page = DevicesPage().open()
        table = devices_page.table.wait_to_load()

        assert_that(table.is_column_sorted(column)).described_as("is column sorted by default").is_false()

        devices_page.sort_asc_by(column)
        sorted_asc_values = table.get_column_values(column)

        assert_that(table.is_up_icon_blue(column)).described_as("is blue sort icon up displayed").is_true()
        assert_that(sorted_asc_values).is_sorted(key=str.lower)

        devices_page.sort_desc_by(column)
        sorted_desc_values = table.get_column_values(column)

        assert_that(table.is_down_icon_blue(column)).described_as("is blue sort icon down displayed").is_true()
        assert_that(sorted_desc_values).is_sorted(key=str.lower, reverse=True)

    @allure.title("3.4.1 Verify that you can search in the search field by all fields")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.issue("filtering doesn't work by status and device type")
    @pytest.mark.parametrize("column", table_columns_provider)
    def test_filter_devices_by_column_value(self, column):
        devices_page = DevicesPage().open()
        table = devices_page.table.wait_to_load()
        devices_page.sort_desc_by(column)
        item = table.get_column_values(column)[0].split()[0]

        devices_page.search_by(item)

        assert_that(table.rows).is_not_empty()

        for table_row in table.rows:
            assert_that(table.is_any_row_cell_contains_text_ignoring_case(table_row, item)).is_true()

    @allure.title("Verify that you can search in the search field by substring")
    @allure.severity(allure.severity_level.NORMAL)
    def test_filter_devices_by_substring(self):
        devices_page = DevicesPage().open()
        table = devices_page.table.wait_to_load()
        init_rows_count = len(table.rows)
        random_device_type = random_list_item(table.get_column_values(DevicesTable.Headers.SERIAL_NUMBER))
        substring = random_device_type[0:4]

        devices_page.search_by(substring)

        assert_that(table.rows).is_not_empty()

        for table_row in table.rows:
            assert_that(table.is_any_row_cell_contains_text_ignoring_case(table_row, substring)).is_true()

        devices_page.click_reset()

        assert_that(devices_page.search_input.is_empty()).described_as("Search input to be empty after reset").is_true()
        assert_that(table.rows).described_as("Table rows count after reset").is_length(init_rows_count)
