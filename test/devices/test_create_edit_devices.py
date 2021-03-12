import allure
import pytest
from assertpy import assert_that

from src.const import Feature
from src.site.components.cascader_picker import SEPARATOR
from src.site.login_page import LoginPage
from src.site.components.tables import DevicesTable
from src.site.pages import DevicesPage
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
        devices_page = self.home_page.left_panel.open_devices()
        headers = DevicesTable.Headers

        new_device = random_device()

        devices_page.add_device(new_device)

        assert_that(devices_page.notification.get_message()).is_equal_to(DevicesPage.DEVICE_CREATED_MESSAGE)

        devices_page.reload().search_by(new_device.serial_number)

        assert_that(devices_page.table.get_column_values(headers.SERIAL_NUMBER)).contains_only(new_device.serial_number)
        assert_that(devices_page.table.get_column_values(headers.DEVICE_TYPE)).contains_only(
            new_device.model + SEPARATOR + new_device.device)
        assert_that(devices_page.table.get_column_values(headers.STATUS)).contains_only(DevicesTable.INACTIVE_STATUS)

        assert_that(devices_page.table.is_device_editable(new_device.serial_number))\
            .described_as("Properties link").is_true()

        edit_dialog = devices_page.open_device_properties_dialog(new_device.serial_number)

        # assert_that(edit_dialog.get_serial_number()).is_equal_to(new_device.serial_number)
        # assert_that(edit_dialog.get_device_type()).contains(new_device.device_type)

    @allure.title("3.4.2 Create new device with all “Customer” fields")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_device_with_customer(self):
        devices_page = self.home_page.left_panel.open_devices()
        headers = DevicesTable.Headers

        new_device = random_device()
        new_customer = random_usa_customer()

        devices_page.add_device(new_device, new_customer)

        assert_that(devices_page.notification.get_message()).is_equal_to(DevicesPage.DEVICE_CREATED_MESSAGE)

        devices_page.reload().search_by(new_device.serial_number)

        assert_that(devices_page.table.get_column_values(headers.SERIAL_NUMBER)).contains_only(new_device.serial_number)
        assert_that(devices_page.table.get_column_values(headers.DEVICE_TYPE)).contains_only(
            new_device.model + SEPARATOR + new_device.device)
        assert_that(devices_page.table.get_column_values(headers.STATUS)).contains_only(DevicesTable.INACTIVE_STATUS)
        assert_that(devices_page.table.get_column_values(headers.CLINIC_ID)).contains_only(new_customer.clinic_id)
        assert_that(devices_page.table.get_column_values(headers.CLINIC_NAME)).contains_only(new_customer.clinic_name)
        assert_that(devices_page.table.get_column_values(headers.COUNTRY)).contains_only(new_customer.region_country)

        edit_dialog = devices_page.open_device_properties_dialog(new_device.serial_number)

        # assert_that(edit_dialog.get_serial_number()).is_equal_to(new_device.serial_number)
        # assert_that(edit_dialog.get_device_type()).contains(new_device.device_type)
