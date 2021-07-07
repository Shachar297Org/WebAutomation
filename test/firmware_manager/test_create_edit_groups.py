import allure
import pytest
from assertpy import assert_that
from selene.support.conditions import be, have

from src.const import Feature, Region, APAC_Country, DeviceGroup, AcupulseDeviceModels, Acupulse30Wdevices
from src.domain.credentials import Credentials
from src.site.components.tables import GroupsTable, GroupDevicesTable
from src.site.components.tree_selector import SEPARATOR
from src.site.dialogs import get_element_label, assert_text_input_default_state, \
    assert_tree_selector_default_state, CreateGroupDialog, GroupDevicesDialog, WarningDialog
from src.site.login_page import LoginPage
from src.site.pages import GroupsPage, DevicesPage
from src.util.driver_util import clear_session_storage, clear_local_storage
from src.util.random_util import random_string, random_list_item
from test.test_data_provider import fota_admin_credentials, random_device, super_admin_credentials


@pytest.fixture(autouse=True)
def cleanup_browser_session():
    yield
    clear_session_storage()
    clear_local_storage()


def login_as(credentials: Credentials):
    LoginPage().open().login_as(credentials)
    return GroupsPage().open()


@allure.feature(Feature.FW_MANAGER)
class TestCreateEditGroups:

    @allure.title("Verify 'Create Group' dialog web elements")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_group_dialog_elements(self):
        groups_page = login_as(fota_admin_credentials)
        dialog = groups_page.click_add_group()

        dialog.title.should(have.exact_text(CreateGroupDialog.TITLE))
        assert_text_input_default_state(dialog.group_name_input, CreateGroupDialog.GROUP_NAME_LABEL)

        assert_that(get_element_label(dialog.device_type_tree_selector.tree_selector)) \
            .described_as("Device type label").is_equal_to(CreateGroupDialog.DEVICE_TYPE_FAMILY_LABEL)
        dialog.device_type_tree_selector.tree_selector.should(be.visible)
        assert_that(dialog.device_type_tree_selector.selected_items()) \
            .described_as("'Device type' tree selector to be empty").is_empty()

        assert_tree_selector_default_state(dialog.locations_tree_selector, CreateGroupDialog.LOCATIONS_PLACEHOLDER)
        assert_that(get_element_label(dialog.locations_tree_selector.tree_selector)).described_as("Locations label") \
            .is_equal_to(CreateGroupDialog.LOCATIONS_LABEL)

        dialog.create_button.should(be.visible).should(be.clickable)
        dialog.cancel_button.should(be.visible).should(be.clickable)

    @allure.title("3.6.2. Create a new group")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_group(self):
        test_group_name = "autotests_" + random_string(8)
        test_region = Region.APAC
        test_country1 = APAC_Country.CHINA
        test_country2 = APAC_Country.INDIA
        test_device_group = DeviceGroup.ACUPULSE
        test_device_model = AcupulseDeviceModels.ACUPULSE_30W
        test_device = Acupulse30Wdevices.GA_0000070CN

        groups_page = login_as(fota_admin_credentials)
        dialog = groups_page.click_add_group()

        dialog.set_group_name(test_group_name) \
            .select_device(test_device) \
            .select_countries(test_region, test_country1, test_country2) \
            .click_create()

        assert_that(groups_page.notification.get_message()).is_equal_to(GroupsPage.GROUP_CREATED_MESSAGE)

        groups_page.reload().search_by(test_group_name)

        assert_that(groups_page.table.get_column_values(GroupsTable.Headers.NAME)).contains(test_group_name)
        created_row = groups_page.table.get_row_by_name(test_group_name)

        assert_that(created_row.get_cell_text(GroupsTable.Headers.DEVICE_TYPE)) \
            .is_equal_to(test_device_group + SEPARATOR + test_device_model + SEPARATOR + test_device)
        assert_that(created_row.get_cell_text(GroupsTable.Headers.REGION)).is_equal_to(test_region)
        assert_that(created_row.get_cell_text(GroupsTable.Headers.COUNTRY)) \
            .is_equal_to(test_country1 + ", " + test_country2)

        assert_that(groups_page.table.is_row_contains_edit_button(created_row)) \
            .described_as("Edit button").is_true()
        assert_that(groups_page.table.is_row_contains_assign_device_button(created_row)) \
            .described_as("Assign device button").is_true()
        assert_that(groups_page.table.is_row_contains_update_version_button(created_row)) \
            .described_as("Update version button").is_true()
        assert_that(groups_page.table.is_row_contains_status_button(created_row)) \
            .described_as("Status button").is_true()

    @allure.title("3.6.3. Edit a group")
    @allure.severity(allure.severity_level.NORMAL)
    def test_edit_group(self):
        test_group_name = "autotests_" + random_string(8)
        test_region = Region.APAC
        test_country = APAC_Country.PAKISTAN
        test_device = Acupulse30Wdevices.GA_0000070GR

        groups_page = login_as(fota_admin_credentials)
        create_dialog = groups_page.click_add_group()

        create_dialog.set_group_name(test_group_name) \
            .select_device(test_device) \
            .select_countries(test_region, test_country) \
            .click_create()
        groups_page.notification.wait_to_disappear()

        edited_group_name = "autotests_" + random_string(8)
        groups_page.reload().search_by(test_group_name)
        edit_dialog = groups_page.click_edit_group(test_group_name)

        edit_dialog.group_name_input.should(be.enabled)
        assert_that(edit_dialog.locations_tree_selector.is_disabled()) \
            .described_as("Locations tree selector to be disabled").is_true()
        assert_that(edit_dialog.device_type_tree_selector.is_disabled()) \
            .described_as("Device type tree selector to be disabled").is_true()

        edit_dialog.set_group_name(edited_group_name).click_update()
        assert_that(groups_page.notification.get_message()).is_equal_to(GroupsPage.GROUP_UPDATED_MESSAGE)
        groups_page.reload().search_by(edited_group_name)
        assert_that(groups_page.table.get_column_values(GroupsTable.Headers.NAME)).contains(edited_group_name)
        edited_row = groups_page.table.get_row_by_name(edited_group_name)

        assert_that(edited_row.get_cell_text(GroupsTable.Headers.DEVICE_TYPE)).contains(test_device)
        assert_that(edited_row.get_cell_text(GroupsTable.Headers.REGION)).is_equal_to(test_region)
        assert_that(edited_row.get_cell_text(GroupsTable.Headers.COUNTRY)).is_equal_to(test_country)

    @allure.title("Verify Groups page web elements")
    @allure.description_html("""
    <ol>
        <li>Open groups page in firmware manager section</li>
        <li>Click 'Assign device' on any group in the table</li>
        <li>Verify that correct group name is displayed</li>
        <li>Verify that the search input is visible, blank and has correct placeholder</li>
        <li>Verify that device and location tree pickers are visible, enabled, empty and have correct placeholder</li>
        <li>Verify that "Reset", "Reload" buttons are visible and clickable</li>
        <li>Verify that groups table is visible, enabled and has correct columns</li>
    </ol>
    """)
    @allure.severity(allure.severity_level.NORMAL)
    def test_assign_device_dialog_elements(self):
        groups_page = login_as(fota_admin_credentials)
        device = random_list_item(groups_page.table.get_column_values(GroupsTable.Headers.NAME))
        group_devices_dialog = groups_page.click_assign_device(device)
        group_devices_dialog.group_name.should(have.text(device))
        headers = GroupDevicesTable.Headers

        group_devices_dialog.search_input.input.should(be.visible).should(be.enabled).should(be.blank)
        assert_that(group_devices_dialog.search_input.get_placeholder()).is_equal_to(groups_page.SEARCH_TEXT)

        group_devices_dialog.device_tree_picker.tree_selector.should(be.visible)
        assert_that(group_devices_dialog.device_tree_picker.is_enabled()) \
            .described_as("'Device Types' tree picker to be enabled").is_true()
        assert_that(group_devices_dialog.device_tree_picker.selected_items()) \
            .described_as("'Device Types' tree picker to be empty").is_empty()
        assert_that(group_devices_dialog.device_tree_picker.get_placeholder()) \
            .is_equal_to(GroupsPage.DEVICE_TYPES_TEXT)

        group_devices_dialog.location_tree_picker.tree_selector.should(be.visible)
        assert_that(group_devices_dialog.location_tree_picker.is_enabled()) \
            .described_as("'Location' tree picker to be enabled").is_true()
        assert_that(group_devices_dialog.location_tree_picker.selected_items()) \
            .described_as("'Location' tree picker to be empty").is_empty()
        assert_that(group_devices_dialog.location_tree_picker.get_placeholder()) \
            .is_equal_to(GroupsPage.LOCATIONS_TEXT)

        group_devices_dialog.reset_button.button.should(be.visible).should(be.clickable)
        group_devices_dialog.reload_button.should(be.visible).should(be.clickable)
        group_devices_dialog.update_device_assignment_button.should(be.visible).should(be.clickable)

        group_devices_dialog.table.table.should(be.visible).should(be.enabled)
        assert_that(group_devices_dialog.table.get_headers()).contains(headers.SERIAL_NUMBER, headers.DEVICE_TYPE,
                                                                       headers.CLINIC_ID, headers.CLINIC_NAME,
                                                                       headers.REGION, headers.COUNTRY)

    @allure.title("3.6.4. Assign a device to the group")
    @allure.severity(allure.severity_level.NORMAL)
    def test_assign_device_to_group(self):
        test_device = random_device()
        test_group_name = "autotests_" + random_string(8)

        login_as(super_admin_credentials)
        DevicesPage().open() \
            .add_device(test_device)

        groups_page = GroupsPage().open()
        self.create_group(groups_page, test_group_name, test_device.device)

        groups_page.reload().search_by(test_group_name)
        group_devices_dialog = groups_page.click_assign_device(test_group_name)
        group_devices_dialog.group_name.should(have.text(test_group_name))
        assert_that(group_devices_dialog.table.get_column_values(GroupDevicesTable.Headers.DEVICE_TYPE)) \
            .described_as("Device types").contains_only(test_device.device)
        group_devices_dialog.select_device_by_serial_number(test_device.serial_number) \
            .click_update()
        assert_that(groups_page.notification.get_message()) \
            .is_equal_to(GroupDevicesDialog.ASSIGNED_DEVICE_TO_GROUP_MESSAGE)

        groups_page.reload().search_by(test_group_name)
        status_dialog = groups_page.click_status(test_group_name)
        assert_that(status_dialog.get_devices()).described_as("Added devices").contains_only(test_device.serial_number)

    @allure.title("3.6.4. Assign already assigned device to group")
    @allure.severity(allure.severity_level.NORMAL)
    def test_assign_assigned_device_to_another_group(self):
        test_device = random_device()
        test_group_1 = "autotests_group_1_" + random_string(8)
        test_group_2 = "autotests_group_2_" + random_string(8)

        login_as(super_admin_credentials)
        DevicesPage().open() \
            .add_device(test_device)

        groups_page = GroupsPage().open()
        self.create_group(groups_page, test_group_1, test_device.device)
        self.create_group(groups_page, test_group_2, test_device.device)

        groups_page.reload().search_by(test_group_1)
        group_devices_dialog = groups_page.click_assign_device(test_group_1)
        group_devices_dialog.select_device_by_serial_number(test_device.serial_number) \
            .click_update()
        groups_page.notification.wait_to_disappear()

        groups_page.search_by(test_group_2)
        group_devices_dialog = groups_page.click_assign_device(test_group_2)
        group_devices_dialog.search_by(test_device.serial_number)
        assert_that(group_devices_dialog.table.is_warn_icon_displayed(test_device.serial_number))\
            .described_as("warn icon to be displayed").is_true()
        group_devices_dialog.table.select_device(test_device.serial_number)

        warning_dialog = WarningDialog().wait_to_load()
        warning_dialog.text.should(have.text(GroupDevicesDialog.get_expected_device_assigned_warning(
            test_device.serial_number, test_group_1)))
        warning_dialog.additional_text.should(have.text(GroupDevicesDialog.CONTINUE_TEXT))
        warning_dialog.click_ok()
        assert_that(group_devices_dialog.table.is_device_selected(test_device.serial_number)) \
            .described_as("Device to be selected").is_true()

        group_devices_dialog.click_update()
        groups_page.search_by(test_group_1)
        group_devices_dialog = groups_page.click_assign_device(test_group_1)
        group_devices_dialog.search_by(test_device.serial_number)
        assert_that(group_devices_dialog.table.is_device_selected(test_device.serial_number))\
            .described_as("Device to be reassigned from the first group").is_false()

    @allure.title("3.6.4. Assign all devices to group")
    @allure.severity(allure.severity_level.NORMAL)
    def test_assign_all_devices_to_group(self):
        test_device = random_device()
        test_group_1 = "autotests_group_1_" + random_string(8)
        test_group_2 = "autotests_group_2_" + random_string(8)

        login_as(super_admin_credentials)
        DevicesPage().open() \
            .add_device(test_device)

        groups_page = GroupsPage().open()
        self.create_group(groups_page, test_group_1, test_device.device)
        self.create_group(groups_page, test_group_2, test_device.device)

        group_devices_dialog = groups_page.reload().search_by(test_group_1)\
            .click_assign_device(test_group_1)
        group_devices_dialog.select_device_by_serial_number(test_device.serial_number) \
            .click_update()
        groups_page.notification.wait_to_disappear()

        group_devices_dialog = groups_page.search_by(test_group_2)\
            .click_assign_device(test_group_2)
        group_devices_dialog.table.click_all()

        warning_dialog = WarningDialog().wait_to_load()
        warning_dialog.text.should(have.text(GroupDevicesDialog.AT_LEAST_ONE_DEVICE_ASSIGNED_MESSAGE))
        warning_dialog.additional_text.should(have.text(GroupDevicesDialog.CONTINUE_TEXT))
        warning_dialog.click_ok()
        for device_sn in group_devices_dialog.table.get_column_values(GroupDevicesTable.Headers.SERIAL_NUMBER):
            assert_that(group_devices_dialog.table.is_device_selected(device_sn))\
                .described_as(device_sn + " device to be selected").is_true()

        group_devices_dialog.close()
        group_devices_dialog = groups_page.search_by(test_group_2)\
            .click_assign_device(test_group_2)
        group_devices_dialog.search_by(test_device.serial_number)
        assert_that(group_devices_dialog.table.is_device_selected(test_device.serial_number)) \
            .described_as("Device to be not assigned if operation is canceled").is_false()

    @staticmethod
    def create_group(groups_page: GroupsPage, group_name: str, device_group):
        create_dialog = groups_page.click_add_group()

        create_dialog.set_group_name(group_name) \
            .select_device(device_group) \
            .select_all_locations() \
            .click_create()
        groups_page.notification.wait_to_disappear()
