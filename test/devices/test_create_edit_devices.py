import allure
import pytest
from assertpy import assert_that
from selene.support.conditions import have, be

from src.const import Feature
from src.const.Acupulse30Wdevices import RG_0000070
from src.domain.device import Customer, Device
from src.site.components.cascader_picker import SEPARATOR, CascaderPicker
from src.site.dialogs import CreateDeviceDialog, get_element_label, assert_text_input_default_state, \
    get_element_error_message
from src.site.login_page import LoginPage
from src.site.components.tables import DevicesTable
from src.site.pages import DevicesPage
from src.util.elements_util import is_input_disabled
from src.util.random_util import random_company, random_alpha_numeric_string, random_gmail_alias_from
from test.test_data_provider import super_admin_credentials, random_device, random_usa_customer, TEST_DEVICE_PREFIX, \
    TEST_GMAIL_ACCOUNT


@pytest.fixture(scope="class")
def login(request):
    home_page = LoginPage().open().login_as(super_admin_credentials)
    if request.cls is not None:
        request.cls.home_page = home_page
    yield home_page


@pytest.mark.usefixtures("login")
@allure.feature(Feature.DEVICES)
class TestCreateEditDevices:

    @allure.title("Verify 'Create Device' dialog web elements")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_device_dialog_elements(self):
        devices_page = DevicesPage().open()
        dialog = devices_page.click_add_device()

        dialog.title.should(have.exact_text(CreateDeviceDialog.TITLE))

        assert_text_input_default_state(dialog.device_serial_number_input,
                                        CreateDeviceDialog.DEVICE_SERIAL_NUMBER_LABEL)
        assert_text_input_default_state(dialog.clinic_name_input, CreateDeviceDialog.CLINIC_NAME_LABEL)
        assert_text_input_default_state(dialog.first_name_input, CreateDeviceDialog.FIRST_NAME_LABEL)
        assert_text_input_default_state(dialog.last_name_input, CreateDeviceDialog.LAST_NAME_LABEL)
        assert_text_input_default_state(dialog.email_input, CreateDeviceDialog.EMAIL_LABEL)
        assert_text_input_default_state(dialog.phone_number_input, CreateDeviceDialog.PHONE_NUMBER_LABEL)
        assert_text_input_default_state(dialog.clinic_id_input, CreateDeviceDialog.CLINIC_ID_LABEL)
        assert_text_input_default_state(dialog.street_input, CreateDeviceDialog.STREET_LABEL)
        assert_text_input_default_state(dialog.street_number_input, CreateDeviceDialog.STREET_NUMBER_LABEL)
        assert_text_input_default_state(dialog.city_input, CreateDeviceDialog.CITY_LABEL)
        assert_text_input_default_state(dialog.postal_zip_input, CreateDeviceDialog.POSTAL_ZIP_LABEL)
        assert_text_input_default_state(dialog.comments_textarea, CreateDeviceDialog.COMMENTS_LABEL)

        self.assert_cascader_picker_default_state(dialog.device_type_picker, CreateDeviceDialog.DEVICE_TYPE_LABEL)
        self.assert_cascader_picker_default_state(dialog.region_country_picker, CreateDeviceDialog.REGION_COUNTRY_LABEL)

        dialog.close_button.should(be.visible).should(be.clickable)
        dialog.create_device_button.should(be.visible).should(be.clickable)
        dialog.cancel_button.should(be.visible).should(be.clickable)

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
        devices_page.add_device(device, customer) \
            .reload() \
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

    @allure.title("Validation: Create the same device twice")
    @allure.severity(allure.severity_level.MINOR)
    def test_create_the_same_device_twice(self):
        devices_page = DevicesPage().open()
        devices_page.search_by(TEST_DEVICE_PREFIX)
        existing_device_serial_number = devices_page.table.get_column_values(DevicesTable.Headers.SERIAL_NUMBER)[0]
        existing_device_type = devices_page.table.get_column_values(DevicesTable.Headers.DEVICE_TYPE)[0].split("/")[-1]
        dialog = devices_page.click_add_device()
        dialog.set_device_serial_number(existing_device_serial_number) \
            .select_device_type_by_keyword(existing_device_type).click_create()

        assert_that(devices_page.notification.get_message()).is_equal_to(DevicesPage.CREATION_FAILURE_MESSAGE)

    @allure.title("Validation: Create the device with empty required fields")
    @allure.severity(allure.severity_level.MINOR)
    def test_create_device_with_empty_required_fields(self):
        devices_page = DevicesPage().open()
        dialog = devices_page.click_add_device()
        dialog.set_clinic_name(random_company())
        dialog.click_create()

        assert_that(dialog.is_visible).is_true()
        assert_that(get_element_error_message(dialog.device_serial_number_input)) \
            .is_equal_to(CreateDeviceDialog.FIELD_IS_REQUIRED_MESSAGE)
        assert_that(get_element_error_message(dialog.device_type_picker.picker)) \
            .is_equal_to(CreateDeviceDialog.FIELD_IS_REQUIRED_MESSAGE)

    @allure.title("Validation: Create the device with too long parameters")
    @allure.severity(allure.severity_level.MINOR)
    def test_create_device_with_too_long_parameters(self):
        devices_page = DevicesPage().open()
        dialog = devices_page.click_add_device()
        dialog.set_device_serial_number(random_alpha_numeric_string(37)) \
            .set_clinic_name(random_alpha_numeric_string(33)) \
            .set_first_name(random_alpha_numeric_string(33)) \
            .set_last_name(random_alpha_numeric_string(33)) \
            .set_phone_number(random_alpha_numeric_string(33)) \
            .set_clinic_id(random_alpha_numeric_string(33)) \
            .set_street(random_alpha_numeric_string(101)) \
            .set_street_number(random_alpha_numeric_string(11)) \
            .set_city(random_alpha_numeric_string(101)) \
            .set_postal_code_zip(random_alpha_numeric_string(13)) \
            .set_comment(random_alpha_numeric_string(257)) \
            .click_create()

        assert_that(dialog.is_visible).is_true()
        assert_that(get_element_error_message(dialog.device_serial_number_input)) \
            .is_equal_to(CreateDeviceDialog.MAX_36_CHARS_ALLOWED_ERROR)
        assert_that(get_element_error_message(dialog.clinic_name_input)) \
            .is_equal_to(CreateDeviceDialog.MAX_32_CHARS_ALLOWED_ERROR)
        assert_that(get_element_error_message(dialog.first_name_input)) \
            .is_equal_to(CreateDeviceDialog.MAX_32_CHARS_ALLOWED_ERROR)
        assert_that(get_element_error_message(dialog.last_name_input)) \
            .is_equal_to(CreateDeviceDialog.MAX_32_CHARS_ALLOWED_ERROR)
        assert_that(get_element_error_message(dialog.phone_number_input)) \
            .is_equal_to(CreateDeviceDialog.MAX_32_CHARS_ALLOWED_ERROR)
        assert_that(get_element_error_message(dialog.clinic_id_input)) \
            .is_equal_to(CreateDeviceDialog.MAX_32_CHARS_ALLOWED_ERROR)
        assert_that(get_element_error_message(dialog.street_input)) \
            .is_equal_to(CreateDeviceDialog.MAX_100_CHARS_ALLOWED_ERROR)
        assert_that(get_element_error_message(dialog.street_number_input)) \
            .is_equal_to(CreateDeviceDialog.MAX_10_CHARS_ALLOWED_ERROR)
        assert_that(get_element_error_message(dialog.city_input)) \
            .is_equal_to(CreateDeviceDialog.MAX_100_CHARS_ALLOWED_ERROR)
        assert_that(get_element_error_message(dialog.postal_zip_input)) \
            .is_equal_to(CreateDeviceDialog.MAX_12_CHARS_ALLOWED_ERROR)
        assert_that(get_element_error_message(dialog.comments_textarea)) \
            .is_equal_to(CreateDeviceDialog.MAX_256_CHARS_ALLOWED_ERROR)

    @allure.title("Validation: Create the device with invalid serial number and customer email")
    @allure.severity(allure.severity_level.MINOR)
    def test_create_device_with_invalid_parameters(self):
        devices_page = DevicesPage().open()
        dialog = devices_page.click_add_device()
        dialog.set_device_serial_number(random_alpha_numeric_string(10) + " " + random_alpha_numeric_string(10)) \
            .select_device_type_by_keyword(RG_0000070) \
            .set_email(random_alpha_numeric_string(10))

        assert_that(get_element_error_message(dialog.email_input)).is_equal_to(CreateDeviceDialog.EMAIL_INVALID_ERROR)

        dialog.set_email(random_gmail_alias_from(TEST_GMAIL_ACCOUNT))
        dialog.click_create()

        assert_that(devices_page.notification.get_message()).is_equal_to(DevicesPage.CREATION_FAILURE_MESSAGE)

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

    @allure.step
    def assert_cascader_picker_default_state(self, picker: CascaderPicker, expected_label: str):
        picker.picker.should(be.visible)
        picker.input.should(be.visible).should(be.clickable).should(be.blank)
        assert_that(picker.is_disabled()).described_as(expected_label + " picker to be disabled").is_false()
        assert_that(picker.get_selected_item()).described_as(expected_label + " picker to be empty").is_empty()
        assert_that(get_element_label(picker.picker)).is_equal_to(expected_label)
