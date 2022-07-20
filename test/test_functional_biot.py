import allure
import pytest
from assertpy import assert_that
from selene.core import query
from selene.support.conditions import have

from src.const import Feature
from src.site.login_page import LoginPage
from selene.api import be
from src.site.components.tables import UsersTable, DeviceAssignmentTable
from src.site.components.tables import DevicesTable, PropertiesTable, AssignUserTable
from src.site.dialogs import CreateDeviceDialog, get_element_label, assert_text_input_default_state, \
    get_element_error_message, DevicePropertiesDialog
from src.site.pages import UsersPage

from src.util.driver_util import *
from test.test_data_provider import super_admin_credentials

from test.test_data_provider import random_user, fota_admin_credentials, TEST_SUPER_ADMIN, \
    TEST_FOTA_ADMIN, TEST_SYSTEM_ENGINEER, TEST_SERVICE_ADMIN, TEST_TECH_SUPPORT, super_admin_credentials, \
    user_for_disabling_credentials
from test.users.base_users_test import BaseUsersTest, login_as
from src.site.pages import DevicesPage, UsersPage
from src.util.elements_util import is_input_disabled
from src.util.random_util import random_company, random_alpha_numeric_string, random_gmail_alias_from, random_list_item
from test.devices.base_devices_test import BaseDevicesTest
from test.test_data_provider import super_admin_credentials, random_device, random_usa_customer, TEST_DEVICE_PREFIX, \
    TEST_GMAIL_ACCOUNT, random_user


USERNAME = super_admin_credentials.username
PASSWORD = super_admin_credentials.password


@pytest.fixture(autouse=True)
def cleanup_browser_session():
    yield
    clear_session_storage()
    clear_local_storage()


@allure.feature(Feature.BIOT_FUNCTIONAL_TESTS)
class TestFunctionalBiot(BaseUsersTest, BaseDevicesTest):

    @allure.title("Verify that a user can login into the portal")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_successful_login(self, cleanup_browser_session):
        home_page = LoginPage().open().login(USERNAME, PASSWORD)

        home_page.left_panel.panel.should(be.present).should(be.clickable)

        print(get_local_storage()) 

    @allure.title("Create a new user")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_user(self):
        users_page = login_as(fota_admin_credentials)
        headers = UsersTable.Headers
        new_user = random_user()

        users_page.add_user(new_user)

        assert_that(users_page.notification.get_message()).is_equal_to(UsersPage.USER_CREATED_MESSAGE)

        users_page.reload().search_by(new_user.email)

        assert_that(users_page.table.get_column_values(headers.EMAIL)).contains(new_user.email)
        user_row = users_page.table.get_row_by_email(new_user.email)
        self.assert_user_row(user_row, new_user)
        assert_that(users_page.table.is_user_editable(new_user.email)).described_as("Edit link").is_true()

        edit_dialog = users_page.open_edit_user_dialog(new_user.email)

        self.assert_user_fields(edit_dialog, new_user)        

    
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
        users_page = login_as(super_admin_credentials)
        new_device = random_device()

        devices_page = DevicesPage().open()
        devices_page.add_device(new_device)

        assert_that(devices_page.notification.get_message()).is_equal_to(DevicesPage.DEVICE_CREATED_MESSAGE)
        devices_page.notification.wait_to_disappear()

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

       

