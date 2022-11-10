import allure
import pytest
from assertpy import assert_that
from selene.support.conditions import be

from src.const import Feature
from src.site.login_page import LoginPage
from src.site.pages import DevicesPage, UsersPage
from test.devices.base_devices_test import BaseDevicesTest
from test.test_data_provider import random_device, random_usa_customer, random_user, fota_admin_credentials


@pytest.fixture(scope="class")
def login():
    LoginPage().open().login_as(fota_admin_credentials)


@pytest.mark.usefixtures("login")
@allure.feature(Feature.PERMISSIONS)
class TestFotaAdminDevicesPermissions(BaseDevicesTest):

    @allure.title("3.1.2.2 View devices in a table")
    @allure.severity(allure.severity_level.NORMAL)
    def test_devices_list(self):
        devices_page = DevicesPage().open()

        devices_page.table.wait_to_load()
        devices_page.table.table.should(be.visible).should(be.enabled)
        assert_that(devices_page.table.get_rows()).is_not_empty()

    @pytest.mark.skip(reason="not an issue, by design")
    @allure.issue("LD-390")
    @allure.title("3.1.2.2 Create and view a new device")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_view_device(self):
        new_device = random_device()
        new_customer = random_usa_customer()

        devices_page = DevicesPage().open()
        devices_page.add_device(new_device, new_customer)

        assert_that(devices_page.notification.get_message()).is_equal_to(DevicesPage.DEVICE_CREATED_MESSAGE)

        devices_page.reload().search_by(new_device.serial_number)

        self.assert_device_in_table(devices_page.table, new_device)
        self.assert_customer_in_table(devices_page.table, new_customer)

        edit_dialog = devices_page.open_device_properties(new_device.serial_number)

        edit_dialog.general_tab.assert_device_fields(new_device)
        edit_dialog.general_tab.assert_customer_fields(new_customer)

    @pytest.mark.skip(reason="not an issue, by design")
    @allure.issue("LD-390")
    @allure.title("3.1.2.2 Edit device customer details")
    @allure.severity(allure.severity_level.NORMAL)
    def test_edit_device_customer_details(self):
        device = random_device()
        customer = random_usa_customer()
        new_customer = random_usa_customer()

        devices_page = DevicesPage().open()
        devices_page.add_device(device, customer) \
            .reload()
        devices_page.search_by(device.serial_number)
        properties_dialog = devices_page.open_device_properties(device.serial_number)
        properties_dialog.general_tab.set_customer_fields(new_customer)
        properties_dialog.general_tab.click_update()

        assert_that(devices_page.notification.get_message()).is_equal_to(DevicesPage.DEVICE_UPDATED_MESSAGE)

        devices_page.reload().search_by(device.serial_number)

        self.assert_device_in_table(devices_page.table, device)
        self.assert_customer_in_table(devices_page.table, new_customer)

        edit_dialog = devices_page.open_device_properties(device.serial_number)

        edit_dialog.general_tab.assert_device_fields(device)
        edit_dialog.general_tab.assert_customer_fields(new_customer)

    @pytest.mark.skip(reason="not an issue, by design")
    @allure.title("3.1.2.2 Assign User")
    @allure.issue("LD-390")
    @allure.issue("LD-392")
    @allure.severity(allure.severity_level.NORMAL)
    def test_assign_user(self):
        test_device = random_device()
        test_user = random_user()

        UsersPage().open().add_user(test_user)

        devices_page = DevicesPage().open().add_device(test_device).wait_to_load()

        devices_page = DevicesPage().open()

        devices_page = devices_page.reload().search_by(test_device.serial_number)
        properties_dialog = devices_page.open_device_properties(test_device.serial_number)

        assign_tab = properties_dialog.assign_tab.open()

        assign_tab.search_by(test_user.name)
        assign_tab.table.wait_to_load().select_user(test_user.name)
        assign_tab.click_update_user_assignment()

        assert_that(devices_page.notification.get_message()).is_equal_to(DevicesPage.DEVICE_UPDATED_MESSAGE)

        properties_dialog = devices_page.open_device_properties(test_device.serial_number)
        properties_dialog.assign_tab.open()
        assert_that(properties_dialog.assign_tab.table.is_user_selected(test_user.name)).is_true()

        users_page = UsersPage().open()
        users_page.search_by(test_user.email)
        edit_user_dialog = users_page.open_edit_user_dialog(test_user.email)

        device_rows = edit_user_dialog.device_table.get_rows()
        assert_that(device_rows).is_not_empty()
        for row in device_rows:
            assert_that(edit_user_dialog.device_table.is_any_row_cell_contains_text_ignoring_case(
                row, test_device.model))
