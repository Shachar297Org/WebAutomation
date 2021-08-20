import allure
import pytest
from assertpy import assert_that
from selene.support.conditions import have, be

from src.const import Feature
from src.const.Acupulse30Wdevices import RG_0000070
from src.site.components.cascader_picker import CascaderPicker
from src.site.components.tables import DevicesTable, PropertiesTable, AssignUserTable
from src.site.dialogs import CreateDeviceDialog, get_element_label, assert_text_input_default_state, \
    get_element_error_message, DevicePropertiesDialog
from src.site.login_page import LoginPage
from src.site.pages import DevicesPage, UsersPage
from src.util.elements_util import is_input_disabled
from src.util.random_util import random_company, random_alpha_numeric_string, random_gmail_alias_from, random_list_item
from test.devices.base_devices_test import BaseDevicesTest
from test.test_data_provider import super_admin_credentials, random_device, random_usa_customer, TEST_DEVICE_PREFIX, \
    TEST_GMAIL_ACCOUNT, random_user


@pytest.fixture(scope="class")
def login(request):
    home_page = LoginPage().open().login_as(super_admin_credentials)
    if request.cls is not None:
        request.cls.home_page = home_page
    yield home_page


@pytest.mark.usefixtures("login")
@allure.feature(Feature.DEVICES)
class TestCreateEditDevices(BaseDevicesTest):

    @allure.title("Verify 'Create Device' dialog web elements")
    @allure.description_html("""
    <ol>
        <li>In the Devices Tab open 'Create Device' dialog</li>
        <li>Verify that the title has a correct text</li>
        <li>Verify that all text fields are visible, blank and have correct labels</li>
        <li>Verify that all cascader pickers are visible, clickable, blank, enabled, have correct labels  </li>
        <li>Verify that "Create Device", "Cancel", "Close" buttons are visible and clickable</li>
    </ol>
    """)
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
    @allure.description_html("""
    <ol>
        <li>In the Devices Tab click on the blue Plus button (on the top left) - A Create Device window will appear</li>
        <li>Enter value in “Device Serial Number” and select a “Device Type”</li>
        <li>Click on the Create Device button - Create Device successful message will appear</li>
        <li>Verify that the new Device created has been added to the Device list</li>
        <li>Open device properties and verify that the "Device Type", “Device Serial Number” correctly displayed</li>
        <li>Verify that the status is inactive and the activation info is empty</li>
        <li>Open "Activation" tab and verify the "Deactivate", "Reactivate" buttons are visible but disabled</li>
    </ol>
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_device(self):
        new_device = random_device()

        devices_page = DevicesPage().open()
        devices_page.add_device(new_device)

        assert_that(devices_page.notification.get_message()).is_equal_to(DevicesPage.DEVICE_CREATED_MESSAGE)

        devices_page.reload().search_by(new_device.serial_number)

        self.assert_device_in_table(devices_page.table, new_device)

        edit_dialog = devices_page.open_device_properties(new_device.serial_number)

        edit_dialog.general_tab.assert_device_fields(new_device)

        edit_dialog.properties_tab.open()

        assert_that(edit_dialog.properties_tab.get_property(PropertiesTable.Property.DEVICE_TYPE)) \
            .is_equal_to(new_device.device)
        assert_that(edit_dialog.properties_tab.get_property(PropertiesTable.Property.DEVICE_SERIAL_NUMBER)) \
            .is_equal_to(new_device.serial_number)
        assert_that(edit_dialog.properties_tab.get_property(PropertiesTable.Property.STATUS)) \
            .is_equal_to(DevicesTable.INACTIVE_STATUS)
        assert_that(edit_dialog.properties_tab.get_property(PropertiesTable.Property.CREATION_TIME)) \
            .is_not_empty()
        assert_that(edit_dialog.properties_tab.get_property(PropertiesTable.Property.LUMENIS_APP_VERSION)) \
            .is_empty()
        assert_that(edit_dialog.properties_tab.get_property(PropertiesTable.Property.ACTIVATION_TYPE)) \
            .is_empty()
        assert_that(edit_dialog.properties_tab.get_property(PropertiesTable.Property.IMEI)) \
            .is_empty()

        edit_dialog.activation_tab.open()

        edit_dialog.activation_tab.device_status.should(be.visible)\
            .should(have.text(DevicePropertiesDialog.DEVICE_STATUS.format(DevicesTable.INACTIVE_STATUS)))
        edit_dialog.activation_tab.deactivate_device_button.should(be.visible).should(be.disabled)
        edit_dialog.activation_tab.reactivate_device_button.should(be.visible).should(be.disabled)

    @allure.title("3.4.2 Create new device with all “Customer” fields")
    @allure.description_html("""
    <ol>
        <li>In the Devices Tab open 'Create Device' dialog</li>
        <li>Enter value in “Device Serial Number” and select a “Device Type”</li>
        <li>Enter values in the “Customer” fields</li>
        <li>In the Region/Country field choose Americas/USA – A new field will appear with a list of US states</li>
        <li>Click on the Create Device button - Create Device successful message will appear</li>
        <li>Verify that the new Device created has been added to the Device list</li>
        <li>Open device properties and verify that the device and customer fields are correctly displayed on the
         "General" tab</li>
    </ol>
    """)
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

        edit_dialog.general_tab.assert_device_fields(new_device)
        edit_dialog.general_tab.assert_customer_fields(new_customer)

    @allure.title("3.4.2 Create new device with customer none-ASCII parameters")
    @allure.description_html("""
    <ol>
        <li>In the Devices Tab open 'Create Device' dialog</li>
        <li>Enter value in “Device Serial Number” and select a “Device Type”</li>
        <li>Enter none-ASCII values in the “Customer” fields</li>
        <li>Click on the Create Device button - Create Device successful message will appear</li>
        <li>Verify that the new Device created has been added to the Device list</li>
        <li>Open device properties and verify that the device and customer fields are correctly displayed</li>
    </ol>
    """)
    @allure.issue("error on creating a device using customer none-ASCII parameters")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_device_using_none_ascii_customer_parameters(self):
        new_device = random_device()
        customer_first_name = "Віктор"
        customer_street = "Шевченка"

        devices_page = DevicesPage().open()
        dialog = devices_page.click_add_device()

        dialog.set_device_serial_number(new_device.serial_number)\
            .select_device_type(new_device)\
            .set_first_name(customer_first_name)\
            .set_street(customer_street)\
            .click_create()

        assert_that(devices_page.notification.get_message()).is_equal_to(DevicesPage.DEVICE_CREATED_MESSAGE)

        devices_page.reload().search_by(new_device.serial_number)

        edit_dialog = devices_page.open_device_properties(new_device.serial_number)

        edit_dialog.general_tab.assert_device_fields(new_device)
        assert_that(edit_dialog.general_tab.get_first_name()).is_equal_to(customer_first_name)
        assert_that(edit_dialog.general_tab.get_street()).is_equal_to(customer_street)

    @allure.title("3.4.3 Edit device")
    @allure.description_html("""
    <ol>
        <li>Preconditions:</li>
        <li>Create a new device</li>
        <li></li>
        <li>In the Devices Tab open 'Create Device' dialog</li>
        <li>Go to Devices Tab click Properties on one of the Devices - An Device Properties window will appear<li>
        <li>Verify you can edit all data except the fields “Device Serial Number” and “Device Type”<li>
        <li>Click on the “Update customer” button - Update Device successful message will appear <li>
        <li>Verify that the edited Device has been updated in the Device list</li>
        <li>Open device properties and verify that the updated device and customer fields are correctly displayed</li>
    </ol>
    """)
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

        assert_that(is_input_disabled(properties_dialog.general_tab.device_serial_number_input)) \
            .described_as("Device serial number input to be disabled").is_true()
        assert_that(properties_dialog.general_tab.device_type_picker.is_disabled()) \
            .described_as("Device type picker to be disabled").is_true()

        properties_dialog.general_tab.set_customer_fields(new_customer)
        properties_dialog.general_tab.click_update()

        assert_that(devices_page.notification.get_message()).is_equal_to(DevicesPage.DEVICE_UPDATED_MESSAGE)

        devices_page.reload().search_by(device.serial_number)

        self.assert_device_in_table(devices_page.table, device)
        self.assert_customer_in_table(devices_page.table, new_customer)

        edit_dialog = devices_page.open_device_properties(device.serial_number)

        edit_dialog.general_tab.assert_device_fields(device)
        edit_dialog.general_tab.assert_customer_fields(new_customer)

    @allure.title("Validation: Create the same device twice")
    @allure.description_html("""
    <ol>
        <li>Try to create a device using the serial number and the device type from the existing device</li>
        <li>Click on the Create Device button</li>
        <li>Verify error message</li>
    </ol>
    """)
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
    @allure.description_html("""
    <ol>
        <li>Try to create a device: leave required fields (serial number device type) empty</li>
        <li>Verify required fields validation messages</li>
    </ol>
    """)
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
    @allure.description_html("""
    <ol>
        <li>Try to create a device: fill in parameters with longer that maximum allowed values</li>
        <li>Verify fields validation messages</li>
    </ol>
    """)
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
    @allure.description_html("""
    <ol>
        <li>Try to create a device: fill in invalid parameters (serial number and email)</li>
        <li>Verify fields validation messages</li>
        <li>Try to use valid but not allowed email</li>
        <li>Click on the Create Device button</li>
        <li>Verify error message</li>
    </ol>
    """)
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
    def assert_cascader_picker_default_state(self, picker: CascaderPicker, expected_label: str):
        picker.picker.should(be.visible)
        picker.input.should(be.visible).should(be.clickable).should(be.blank)
        assert_that(picker.is_disabled()).described_as(expected_label + " picker to be disabled").is_false()
        assert_that(picker.get_selected_item()).described_as(expected_label + " picker to be empty").is_empty()
        assert_that(get_element_label(picker.picker)).is_equal_to(expected_label)


@pytest.mark.usefixtures("login")
@allure.feature(Feature.DEVICES)
class TestDeviceProperties:
    assign_table_columns_provider = [
        AssignUserTable.Headers.NAME,
        AssignUserTable.Headers.USER_GROUP
        ]

    @allure.title("3.4.5 Assign User")
    @allure.description_html("""
    <ol>
        <li>Preconditions:</li>
        <li>Create a new user</li>
        <li>Create a new device</li>
        <li></li>
        <li>Go to Devices Tab click Properties on the created Device - An Device Properties window will appear</li>
        <li>In Device Properties go to “Assign” tab</li>
        <li>Verify that no users assigned to the device yet</li>
        <li>Mark a created user – The Check box will turn blue</li>
        <li>Click on the “Update User Assignment” button - Update Device successful message will appear</li>
        <li>Go back to Properties window – the User you added is marked</li>
        <li>Go to Users Tab change the ?? of the User- the User wont be selected in the Assign  tab of the Device – the
         user isn’t selected</li>
        <li>Open user page, search and open created user and check that the device is in the assigned devices list</li>
    </ol>
    """)
    @allure.issue("The device isn't appeared for the user in the Users device assignment if assign the user"
                  " to the device on  the devices tab")
    @allure.severity(allure.severity_level.NORMAL)
    def test_assign_user(self):
        test_device = random_device()
        test_user = random_user()

        UsersPage().open().add_user(test_user)

        devices_page = DevicesPage().open().add_device(test_device)

        properties_dialog = devices_page.reload().search_by(test_device.serial_number)\
            .open_device_properties(test_device.serial_number)
        assign_tab = properties_dialog.assign_tab.open()

        table = assign_tab.table.wait_to_load()
        users = table.get_column_values(AssignUserTable.Headers.NAME)
        for user in users:
            assert_that(table.is_user_selected(user)).is_false()

        assign_tab.search_by(test_user.name)
        table.select_user(test_user.name)
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

    @allure.title("Sort users by name on Assign Tab of the Device Properties dialog")
    @allure.description_html("""
    <ol>
        <li>Open "Device Properties" "Assign" Tab</li>
        <li>Sort users in the ascending order - Verify users are sorted</li>
        <li>Sort users in the descending order - Verify users are sorted</li>
    </ol>
    """)
    @allure.issue("wrong sorting order if the item contains more than 1 word. The second word isn't considered")
    @allure.severity(allure.severity_level.NORMAL)
    def test_sort_users_on_properties_assign_tab(self):
        assign_tab = self.open_assign_user_dialog()
        table = assign_tab.table.wait_to_load()
        column = AssignUserTable.Headers.NAME

        assert_that(table.is_column_sorted(column)).described_as("is column sorted by default").is_false()

        assign_tab.sort_asc_by_name()
        sorted_asc_values = table.get_column_values(column)

        assert_that(table.is_up_icon_blue(column)).described_as("is blue sort icon up displayed").is_true()
        assert_that(sorted_asc_values).is_sorted(key=str.lower)

        assign_tab.sort_desc_by_name()

        sorted_desc_values = table.get_column_values(column)

        assert_that(table.is_down_icon_blue(column)).described_as("is blue sort icon down displayed").is_true()
        assert_that(sorted_desc_values).is_sorted(key=str.lower, reverse=True)

    @allure.title("Verify that you can search users by any column value")
    @allure.description_html("""
    <ol>
        <li>Open "Device Properties" "Assign" Tab</li>
        <li>Filter users by a column value - Verify users are filtered</li>
    </ol>
    """)
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("column", assign_table_columns_provider)
    def test_filter_users_by_column_value_on_properties_assign_tab(self, column):
        assign_tab = self.open_assign_user_dialog()
        table = assign_tab.table.wait_to_load()
        random_item = random_list_item(table.get_column_values(column)).split()[0]

        assign_tab.search_by(random_item)

        assert_that(table.get_rows()).is_not_empty()
        for table_row in table.get_rows():
            assert_that(table.is_any_row_cell_contains_text_ignoring_case(table_row, random_item)).is_true()

    @allure.title("Verify that you can filter users by 'User Group'")
    @allure.description_html("""
    <ol>
        <li>Open "Device Properties" "Assign" Tab</li>
        <li>Filter users by group - Verify users are filtered</li>
        <li>Click 'Reset' - Verify users aren't filtered</li>
    </ol>
    """)
    @allure.severity(allure.severity_level.NORMAL)
    def test_filter_users_by_user_group_on_properties_assign_tab(self):
        assign_tab = self.open_assign_user_dialog()
        table = assign_tab.table.wait_to_load()
        init_rows_count = len(table.get_rows())
        random_group = random_list_item(table.get_column_values(AssignUserTable.Headers.USER_GROUP))

        assign_tab.filter_by_group(random_group)

        assert_that(table.get_column_values(AssignUserTable.Headers.USER_GROUP)).contains_only(random_group)

        assign_tab.reset()

        assert_that(table.get_rows()).described_as("Table rows count after reset").is_length(init_rows_count)

    @allure.title("Assign users pagination test")
    @allure.description_html("""
    <ol>
        <li>Open "Device Properties" "Assign" Tab</li>
        <li>Verify the pagination component is displayed</li>
        <li>Verify that 10 items displayed on the page and active page number is 1</li>
        <li>Verify that the left arrow is disabled, and right arrow is enabled</li>
        <li>Open the second page</li>
        <li>Verify that the active page number is 2</li>
        <li>Verify that the left arrow became enabled</li>
    </ol>
    """)
    @allure.severity(allure.severity_level.NORMAL)
    def test_users_pagination(self):
        assign_tab = self.open_assign_user_dialog()

        pagination_element = assign_tab.pagination_element
        first_page_items = assign_tab.table.wait_to_load().get_column_values(AssignUserTable.Headers.NAME)

        pagination_element.element.should(be.visible).should(be.enabled)
        assert_that(first_page_items).is_length(10)
        assert_that(pagination_element.get_active_item_number()).is_equal_to(1)
        assert_that(pagination_element.is_left_arrow_disabled())\
            .described_as("'Left arrow' to be disabled by default").is_true()
        assert_that(pagination_element.is_right_arrow_disabled()) \
            .described_as("'Right arrow' to be disabled by default").is_false()

        pagination_element.open_page(2)
        second_page_items = assign_tab.table.wait_to_load().get_column_values(AssignUserTable.Headers.NAME)

        assert_that(pagination_element.get_active_item_number()).is_equal_to(2)
        assert_that(pagination_element.is_left_arrow_disabled()) \
            .described_as("'Left arrow' to be disabled").is_false()
        assert_that(second_page_items).is_not_equal_to(first_page_items)

        pagination_element.open_page(1)
        assert_that(pagination_element.get_active_item_number()).is_equal_to(1)
        assert_that(pagination_element.is_left_arrow_disabled()) \
            .described_as("'Left arrow' to be disabled").is_true()
        assert_that(assign_tab.table.wait_to_load().get_column_values(AssignUserTable.Headers.NAME))\
            .is_equal_to(first_page_items)

    @allure.step
    def open_assign_user_dialog(self) -> DevicePropertiesDialog.AssignTab:
        devices_page = DevicesPage().open().search_by(TEST_DEVICE_PREFIX)

        first_device = devices_page.table.get_column_values(AssignUserTable.Headers.NAME)[0]
        dialog = devices_page.open_device_properties(first_device)
        dialog.assign_tab.open()
        return dialog.assign_tab
