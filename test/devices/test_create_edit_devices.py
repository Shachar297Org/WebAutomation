import allure
import pytest
from assertpy import assert_that

from src.const import Feature
from src.domain.device import Customer, Device
from src.site.components.cascader_picker import SEPARATOR
from src.site.login_page import LoginPage
from src.site.components.tables import DevicesTable
from src.site.pages import DevicesPage
from src.util.elements_util import is_input_disabled
from test.test_data_provider import super_admin_credentials, random_device, random_usa_customer


@pytest.fixture(scope="class")
def login(request):
    home_page = LoginPage().open().login_as(super_admin_credentials)
    if request.cls is not None:
        request.cls.home_page = home_page
    yield home_page


@pytest.mark.usefixtures("login")
@allure.feature(Feature.DEVICES)
class TestCreateEditDevices:

    @allure.title("3.4.2 Create new device")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_device(self):
        new_device = random_device()

        devices_page = DevicesPage().open()
        devices_page.add_device(new_device)

        assert_that(devices_page.notification.get_message()).is_equal_to(DevicesPage.DEVICE_CREATED_MESSAGE)

        devices_page.reload().search_by(new_device.serial_number)

        self.assert_device_in_table(devices_page.table, new_device)

        edit_dialog = devices_page.open_device_properties(new_device.serial_number)

        edit_dialog.general.assert_device_fields(new_device)

    @allure.title("3.4.2 Create new device with all “Customer” fields")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_device_with_customer(self):
        new_device = random_device()
        new_customer = random_usa_customer()

        devices_page = DevicesPage().open()
        devices_page.add_device(new_device, new_customer)

        assert_that(devices_page.notification.get_message()).is_equal_to(DevicesPage.DEVICE_CREATED_MESSAGE)

        devices_page.reload().search_by(new_device.serial_number)

        self.assert_device_in_table(devices_page.table, new_device)
        self.assert_customer_in_table(devices_page.table, new_customer)

        edit_dialog = devices_page.open_device_properties(new_device.serial_number)

        edit_dialog.general.assert_device_fields(new_device)
        edit_dialog.general.assert_customer_fields(new_customer)

    @allure.title("3.4.3 Edit device")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_edit_device(self):
        device = random_device()
        customer = random_usa_customer()
        new_customer = random_usa_customer()

        devices_page = DevicesPage().open()
        devices_page.add_device(device, customer)\
            .reload()\
            .search_by(device.serial_number)
        properties_dialog = devices_page.open_device_properties(device.serial_number)

        assert_that(is_input_disabled(properties_dialog.general.device_serial_number_input)) \
            .described_as("Device serial number input to be disabled").is_true()
        assert_that(properties_dialog.general.device_type_picker.is_disabled()) \
            .described_as("Device type picker to be disabled").is_true()

        properties_dialog.general.set_customer_fields(new_customer)
        properties_dialog.general.click_update()

        assert_that(devices_page.notification.get_message()).is_equal_to(DevicesPage.DEVICE_UPDATED_MESSAGE)

        devices_page.reload().search_by(device.serial_number)

        self.assert_device_in_table(devices_page.table, device)
        self.assert_customer_in_table(devices_page.table, new_customer)

        edit_dialog = devices_page.open_device_properties(device.serial_number)

        edit_dialog.general.assert_device_fields(device)
        edit_dialog.general.assert_customer_fields(new_customer)

    @allure.step
    def assert_device_in_table(self, table: DevicesTable, expected: Device):
        assert_that(table.get_column_values(table.Headers.SERIAL_NUMBER)).contains_only(expected.serial_number)
        assert_that(table.get_column_values(table.Headers.DEVICE_TYPE)).contains_only(
            expected.model + SEPARATOR + expected.device)
        assert_that(table.get_column_values(table.Headers.STATUS)).contains_only(table.INACTIVE_STATUS)
        assert_that(table.is_device_editable(expected.serial_number)).described_as("Properties link").is_true()

    @allure.step
    def assert_customer_in_table(self, table: DevicesTable, expected: Customer):
        assert_that(table.get_column_values(table.Headers.CLINIC_ID)).contains_only(expected.clinic_id)
        assert_that(table.get_column_values(table.Headers.CLINIC_NAME)).contains_only(expected.clinic_name)
        assert_that(table.get_column_values(table.Headers.COUNTRY)).contains_only(expected.region_country)

