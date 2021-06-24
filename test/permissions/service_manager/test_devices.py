import allure
import pytest
from assertpy import assert_that
from selene.support.conditions import be, have

from src.const import Feature
from src.site.components.tables import DevicesTable, PropertiesTable
from src.site.dialogs import DevicePropertiesDialog
from src.site.login_page import LoginPage
from src.site.pages import DevicesPage
from src.util.driver_util import clear_session_storage, clear_local_storage
from test.devices.base_devices_test import BaseDevicesTest
from test.test_data_provider import random_device, random_usa_customer, service_manager_credentials, \
    fota_admin_credentials


@pytest.fixture(autouse=True)
def cleanup_browser_session():
    yield
    clear_session_storage()
    clear_local_storage()


@allure.feature(Feature.PERMISSIONS)
class TestServiceManagerDevicesPermissions(BaseDevicesTest):

    @allure.title("3.1.8.2 View devices in a table")
    @allure.severity(allure.severity_level.NORMAL)
    def test_devices_list(self):
        LoginPage().open().login_as(service_manager_credentials)

        devices_page = DevicesPage().open()

        devices_page.table.wait_to_load()
        devices_page.table.table.should(be.visible).should(be.enabled)
        assert_that(devices_page.table.get_rows()).is_not_empty()

        devices_page.add_button.should(be.not_.present)

        for table_row in devices_page.table.get_rows():
            assert_that(devices_page.table.is_row_contains_properties_button(table_row)).is_true()

    @allure.title("3.1.8.2 View device properties, alarms list, activation status")
    @allure.severity(allure.severity_level.NORMAL)
    def test_device_properties(self):
        new_device = random_device()
        new_customer = random_usa_customer()

        LoginPage().open().login_as(fota_admin_credentials)
        devices_page = DevicesPage().open()
        devices_page.add_device(new_device, new_customer)
        assert_that(devices_page.notification.get_message()).is_equal_to(DevicesPage.DEVICE_CREATED_MESSAGE)
        clear_session_storage()
        clear_local_storage()

        LoginPage().open().login_as(service_manager_credentials)
        devices_page = DevicesPage().open()
        devices_page.search_by(new_device.serial_number)

        self.assert_device_in_table(devices_page.table, new_device)
        self.assert_customer_in_table(devices_page.table, new_customer)

        properties_dialog = devices_page.open_device_properties(new_device.serial_number)

        properties_dialog.general_tab.assert_device_fields(new_device)
        properties_dialog.general_tab.assert_customer_fields(new_customer)

        properties_dialog.general_tab.device_serial_number_input.should(be.disabled)
        properties_dialog.general_tab.clinic_name_input.should(be.disabled)
        properties_dialog.general_tab.first_name_input.should(be.disabled)
        properties_dialog.general_tab.last_name_input.should(be.disabled)
        properties_dialog.general_tab.email_input.should(be.disabled)
        properties_dialog.general_tab.phone_number_input.should(be.disabled)
        properties_dialog.general_tab.comments_textarea.should(be.disabled)
        properties_dialog.general_tab.clinic_id_input.should(be.disabled)
        properties_dialog.general_tab.street_input.should(be.disabled)
        properties_dialog.general_tab.street_number_input.should(be.disabled)
        properties_dialog.general_tab.city_input.should(be.disabled)
        properties_dialog.general_tab.postal_zip_input.should(be.disabled)

        assert_that(properties_dialog.general_tab.device_type_picker.is_disabled()) \
            .described_as("Device type picker to be disabled").is_true()
        assert_that(properties_dialog.general_tab.region_country_picker.is_disabled()) \
            .described_as("Region/ Country picker to be disabled").is_true()
        assert_that(properties_dialog.general_tab.state_select.is_disabled()) \
            .described_as("State select to be disabled").is_true()

        properties_dialog.properties_tab.open()

        assert_that(properties_dialog.properties_tab.get_property(PropertiesTable.Property.DEVICE_TYPE)) \
            .is_equal_to(new_device.device)
        assert_that(properties_dialog.properties_tab.get_property(PropertiesTable.Property.DEVICE_SERIAL_NUMBER)) \
            .is_equal_to(new_device.serial_number)
        assert_that(properties_dialog.properties_tab.get_property(PropertiesTable.Property.STATUS)) \
            .is_equal_to(DevicesTable.INACTIVE_STATUS)
        assert_that(properties_dialog.properties_tab.get_property(PropertiesTable.Property.CREATION_TIME)) \
            .is_not_empty()

        properties_dialog.alarms_history_tab.open()

        properties_dialog.alarms_history_tab.table.table.should(be.visible)

        properties_dialog.activation_tab.open()

        properties_dialog.activation_tab.device_status.should(be.visible) \
            .should(have.text(DevicePropertiesDialog.DEVICE_STATUS.format(DevicesTable.INACTIVE_STATUS)))
        properties_dialog.activation_tab.deactivate_device_button.should(be.visible).should(be.disabled)
        properties_dialog.activation_tab.reactivate_device_button.should(be.visible).should(be.disabled)
