import allure
import pytest
from assertpy import assert_that
from selene.support.conditions import be, have

from src.const import Feature, Region, APAC_Country, DeviceGroup, AcupulseDeviceModels, Acupulse30Wdevices, \
    AmericasCountry
from src.domain.credentials import Credentials
from src.site.components.tables import GroupsTable, GroupDevicesTable, LumenisXVersionTable, GroupDevicesStatusTable
from src.site.components.tree_selector import SEPARATOR
from src.site.dialogs import get_element_label, assert_text_input_default_state, \
    assert_tree_selector_default_state, CreateGroupDialog, GroupDevicesDialog, WarningDialog, UpdateGroupVersionsDialog
from src.site.login_page import LoginPage
from src.site.pages import GroupsPage, DevicesPage, LumenisXVersionPage
from src.util.driver_util import clear_session_storage, clear_local_storage
from src.util.random_util import random_string, random_list_item
from test.test_data_provider import fota_admin_credentials, random_device, super_admin_credentials,\
    random_usa_customer, random_customer

TEST_GROUP_PREFIX = "autotests_"


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
    table_columns_provider = [
        GroupDevicesTable.Headers.SERIAL_NUMBER,
        GroupDevicesTable.Headers.DEVICE_TYPE,
        GroupDevicesTable.Headers.CLINIC_ID,
        GroupDevicesTable.Headers.CLINIC_NAME,
        GroupDevicesTable.Headers.REGION,
        GroupDevicesTable.Headers.COUNTRY
    ]

    @allure.title("Verify 'Create Group' dialog web elements")
    @allure.description_html("""
    <ol>
        <li>Open groups page in firmware manager section</li>
        <li>Click on "+" button to open "Create new group" dialog</li>
        <li>Verify that group title is correct</li>
        <li>Verify that device and location tree pickers are visible, enabled, empty and have correct placeholder</li>
        <li>Verify that "Create", "Cancel" buttons are visible and clickable</li>
    </ol>
    """)
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

    @allure.description_html("""
    <ol>
        <li>In the “Firmware Manager/Groups” tab click on the blue plus button – A “Create Group” Window will open</li>
        <li>Enter the “Group Name”, and select the “Device Type / Family” and “Locations”</li>
        <li>Click on the “Create” button – A message will appear “Create Group successful”</li>
        <li>Verify the created group</li>
    </ol>
    """)
    @allure.title("3.6.2. Create a new group")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_group(self):
        test_group_name = TEST_GROUP_PREFIX + random_string(8)
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

    @allure.description_html("""
    <ol>
        <li>Create a new group</li>
        <li>On the created group click on Edit – A “Edit Group” window will open</li>
        <li>Verify you can edit “Group Name”</li>
        <li>Click on the “Update” button – “Updated group successfully” message will appear</li>
        <li>Verify the edited group</li>
    </ol>
    """)
    @allure.title("3.6.3. Edit a group")
    @allure.severity(allure.severity_level.NORMAL)
    def test_edit_group(self):
        test_group_name = TEST_GROUP_PREFIX + random_string(8)
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

    @allure.description_html("""
    <ol>
        <li>Create a new device with customer fields</li>
        <li>Create a new group with the device type to match the created device</li>
        <li>On the Groups page click "Assign device"</li>
        <li>Verify that group name displayed is correct</li>
        <li>Verify that the device row contains all correct data</li>
        <li>Click update - verify notification message</li>
        <li>Verify that the device is assigned to te group</li>
    </ol>
    """)
    @allure.title("3.6.4. Assign a device to the group")
    @allure.severity(allure.severity_level.NORMAL)
    def test_assign_device_to_group(self):
        test_device = random_device()
        test_customer = random_customer()
        test_group_name = TEST_GROUP_PREFIX + random_string(8)

        login_as(super_admin_credentials)
        DevicesPage().open() \
            .add_device(test_device, test_customer)

        groups_page = GroupsPage().open()
        self.create_group(groups_page, test_group_name, test_device.device)

        groups_page.reload().search_by(test_group_name)
        group_devices_dialog = groups_page.click_assign_device(test_group_name)
        group_devices_dialog.group_name.should(have.text(test_group_name))
        assert_that(group_devices_dialog.table.get_column_values(GroupDevicesTable.Headers.DEVICE_TYPE)) \
            .described_as("Device types").contains_only(test_device.device)

        test_device_row = group_devices_dialog.table.get_row_by_serial_number(test_device.serial_number)
        headers = GroupDevicesTable.Headers
        assert_that(test_device_row.get_cell_text(headers.DEVICE_TYPE)).is_equal_to(test_device.device)
        assert_that(test_device_row.get_cell_text(headers.CLINIC_ID)).is_equal_to(test_customer.clinic_id)
        assert_that(test_device_row.get_cell_text(headers.CLINIC_NAME)).is_equal_to(test_customer.clinic_name)
        assert_that(test_device_row.get_cell_text(headers.REGION)).is_equal_to(Region.EMEA)
        assert_that(test_device_row.get_cell_text(headers.COUNTRY)).is_equal_to(test_customer.region_country)

        group_devices_dialog.select_device_by_serial_number(test_device.serial_number).click_update()
        assert_that(groups_page.notification.get_message()) \
            .is_equal_to(GroupDevicesDialog.ASSIGNED_DEVICE_TO_GROUP_MESSAGE)

        groups_page.reload().search_by(test_group_name)
        status_dialog = groups_page.click_status(test_group_name)
        assert_that(status_dialog.get_devices()).described_as("Added devices").contains_only(test_device.serial_number)

    @allure.description_html("""
    <ol>
        <li>Create a new device</li>
        <li>Create a new group 1</li>
        <li>Create a new group 2</li>
        <li>Assign the device to the group 1</li>
        <li>On the Groups page click "Assign device" for the group 2</li>
        <li>Verify that a Device that is already assigned another group will be marked with a warning red triangle</li>
        <li>Click on the assigned device – A warning message will appear “At least one device is already assigned
         to a group, Are you sure you want to continue?” </li>
         <li>Click "Yes"</li>
        <li>Verify that the device is assigned now to te group 2</li>
        <li>Verify that the device isn't assigned to te group 1 anymore</li>
    </ol>
    """)
    @allure.title("3.6.4. Assign already assigned device to group")
    @allure.severity(allure.severity_level.NORMAL)
    def test_assign_assigned_device_to_another_group(self):
        test_device = random_device()
        test_group_1 = TEST_GROUP_PREFIX + "group_1_" + random_string(8)
        test_group_2 = TEST_GROUP_PREFIX + "group_2_" + random_string(8)

        login_as(super_admin_credentials)
        DevicesPage().open() \
            .add_device(test_device, random_usa_customer())

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
        assert_that(group_devices_dialog.table.is_warn_icon_displayed(test_device.serial_number)) \
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
        assert_that(group_devices_dialog.table.is_device_selected(test_device.serial_number)) \
            .described_as("Device to be reassigned from the first group").is_false()

    @allure.description_html("""
    <ol>
        <li>Create a new device</li>
        <li>Create a new group 1</li>
        <li>Create a new group 2</li>
        <li>Assign the device to the group 1</li>
        <li>On the Groups page click "Assign device" for the group 2</li>
        <li>Click on the “All” button – A warning message will appear “At least one device is already assigned
         to a group, Are you sure you want to continue?” </li>
        <li>Click "Yes" - verify that all devices are selected</li>
        <li>Close the dialog</li>
        <li>Verify that the device isn't assigned to te group 2 if the assign operation wasn't completed</li>
    </ol>
    """)
    @allure.title("3.6.4. Assign all devices to group")
    @allure.severity(allure.severity_level.NORMAL)
    def test_assign_all_devices_to_group(self):
        test_device = random_device()
        test_group_1 = TEST_GROUP_PREFIX + "group_1_" + random_string(8)
        test_group_2 = TEST_GROUP_PREFIX + "group_2_" + random_string(8)

        login_as(super_admin_credentials)
        DevicesPage().open() \
            .add_device(test_device)

        groups_page = GroupsPage().open()
        self.create_group(groups_page, test_group_1, test_device.device)
        self.create_group(groups_page, test_group_2, test_device.device)

        group_devices_dialog = groups_page.reload().search_by(test_group_1) \
            .click_assign_device(test_group_1)
        group_devices_dialog.select_device_by_serial_number(test_device.serial_number) \
            .click_update()
        groups_page.notification.wait_to_disappear()

        group_devices_dialog = groups_page.search_by(test_group_2) \
            .click_assign_device(test_group_2)
        group_devices_dialog.table.click_all()

        warning_dialog = WarningDialog().wait_to_load()
        warning_dialog.text.should(have.text(GroupDevicesDialog.AT_LEAST_ONE_DEVICE_ASSIGNED_MESSAGE))
        warning_dialog.additional_text.should(have.text(GroupDevicesDialog.CONTINUE_TEXT))
        warning_dialog.click_ok()
        for device_sn in group_devices_dialog.table.get_column_values(GroupDevicesTable.Headers.SERIAL_NUMBER):
            assert_that(group_devices_dialog.table.is_device_selected(device_sn)) \
                .described_as(device_sn + " device to be selected").is_true()

        group_devices_dialog.close()
        group_devices_dialog = groups_page.search_by(test_group_2) \
            .click_assign_device(test_group_2)
        group_devices_dialog.search_by(test_device.serial_number)
        assert_that(group_devices_dialog.table.is_device_selected(test_device.serial_number)) \
            .described_as("Device to be not assigned if operation is canceled").is_false()

    @allure.title("3.6.4 Verify that you can sort device rows by any column")
    @allure.description_html("""
    <ol>
        <li>Open groups page</li>
        <li>Open 'Group Devices' dialog</li>
        <li>Sort devices in the ascending order - Verify devices are sorted</li>
        <li>Sort devices in the descending order - Verify devices are sorted</li>
    </ol>
    """)
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("column", table_columns_provider)
    def test_sort_devices(self, column):
        groups_page = login_as(fota_admin_credentials)
        group_devices_dialog = self.open_random_device(groups_page)
        table = group_devices_dialog.table.wait_to_load()

        assert_that(table.is_column_sorted(column)).described_as("is column sorted by default").is_false()

        group_devices_dialog.sort_asc_by(column)
        sorted_asc_values = table.get_column_values(column)

        assert_that(table.is_up_icon_blue(column)).described_as("is blue sort icon up displayed").is_true()
        assert_that(sorted_asc_values).is_sorted(key=str.lower)

        group_devices_dialog.sort_desc_by(column)
        sorted_desc_values = table.get_column_values(column)

        assert_that(table.is_down_icon_blue(column)).described_as("is blue sort icon down displayed").is_true()
        assert_that(sorted_desc_values).is_sorted(key=str.lower, reverse=True)

    @allure.title("3.6.4 Verify that you can search in the search field by all fields")
    @allure.description_html("""
        <ol>
            <li>Open groups page</li>
            <li>Open 'Group Devices' dialog</li>
            <li>Filter devices by a column value - Verify devices are filtered</li>
        </ol>
        """)
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("column", table_columns_provider)
    def test_filter_devices_by_column_value(self, column):
        groups_page = login_as(super_admin_credentials)
        group_devices_dialog = self.open_random_device(groups_page)
        table = group_devices_dialog.table.wait_to_load()

        group_devices_dialog.sort_desc_by(column)
        item = table.get_column_values(column)[0].split()[0]

        group_devices_dialog.search_by(item)

        assert_that(table.get_rows()).is_not_empty()

        for table_row in table.get_rows():
            assert_that(table.is_any_row_cell_contains_text_ignoring_case(table_row, item)).is_true()

    @allure.title("3.6.4 Verify that rows can be filtered by “Device Type” in the designated field ")
    @allure.description_html("""
    <ol>
        <li>Open groups page</li>
        <li>Open 'Group Devices' dialog</li>
        <li>Filter devices by device model - Verify devices are filtered</li>
        <li>Click 'Reset'</li>
        <li>Verify devices aren't filtered</li>
    </ol>
    """)
    @allure.severity(allure.severity_level.NORMAL)
    def test_filter_devices_by_device_model(self):
        test_device_group = DeviceGroup.ACUPULSE
        test_device_model = AcupulseDeviceModels.ACUPULSE_30W

        groups_page = login_as(fota_admin_credentials)
        group_devices_dialog = self.open_random_device(groups_page)
        table = group_devices_dialog.table.wait_to_load()

        group_devices_dialog.device_tree_picker.select_device_models(test_device_group, test_device_model).close()

        assert_that(table.wait_to_load().get_column_values(GroupsTable.Headers.DEVICE_TYPE)) \
            .is_subset_of([Acupulse30Wdevices.GA_0000070CN, Acupulse30Wdevices.GA_0000070GR,
                           Acupulse30Wdevices.RG_0000070, Acupulse30Wdevices.GA_0000070,
                           Acupulse30Wdevices.GA_0000070DE])

        group_devices_dialog.reset()

        assert_that(group_devices_dialog.device_tree_picker.get_all_selected_items()) \
            .described_as("Search input to be empty after reset").is_empty()

    @pytest.mark.skip(reason="Fix later by including creating user, device, adding it to group, etc")
    @allure.title("3.6.4 Verify that rows can be filtered by “Locations” in the designated field")
    @allure.description_html("""
    <ol>
        <li>Open groups page</li>
        <li>Open 'Group Devices' dialog</li>
        <li>Filter devices by location - Verify groups are filtered</li>
        <li>Click 'Reset'</li>
        <li>Verify devices aren't filtered</li>
    </ol>
    """)
    @allure.severity(allure.severity_level.NORMAL)
    def test_filter_devices_by_locations(self):
        test_country = AmericasCountry.USA
        groups_page = login_as(fota_admin_credentials)
        group_devices_dialog = self.open_random_device(groups_page)
        table = group_devices_dialog.table.wait_to_load()

        group_devices_dialog.location_tree_picker.select_countries(Region.AMERICAS, test_country).close()

        assert_that(table.get_column_values(GroupsTable.Headers.COUNTRY)).contains_only(test_country)

        group_devices_dialog.reset()

        assert_that(group_devices_dialog.location_tree_picker.get_all_selected_items()) \
            .described_as("Search input to be empty after reset").is_empty()

    @allure.title("3.6.5 Update Group Versions")
    @allure.description_html("""
    <ol>
        <li>On one of the Groups, click on “Update Versions” – A “Update Group Versions” window will open</li>
        <li>Click on the “LumenisX version” dropdown list – A list of valid LumX versions is will display
             in ascending order</li>
        <li>Verify versions dialog webelements</li>
        <li>Verify that only version that are defined “Valid” on the “LumenisX Version“ window appear in the list'</li>
        <li>Select a Version from the list and click on the “Publish Update” button – A message “Version published
             to group successfully” will appear</li>
        <li>On the Groups page table verify that the version is added to the group</li>
    </ol>
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    def test_update_group_version(self):
        login_as(fota_admin_credentials)
        version_page = LumenisXVersionPage().open()
        version_page.filter_valid()
        valid_version = self.get_first_version_from_table(version_page.table)
        version_page.filter_invalid()
        invalid_version = self.get_first_version_from_table(version_page.table)

        groups_page = GroupsPage().open()
        groups_page.search_by(TEST_GROUP_PREFIX)
        group = random_list_item(groups_page.table.get_column_values(GroupsTable.Headers.NAME))
        versions_dialog = groups_page.click_update_versions(group)

        versions_dialog.title.should(have.exact_text(UpdateGroupVersionsDialog.TITLE))
        versions_dialog.group_name_input.should(be.visible).should(be.not_.enabled)
        versions_dialog.software_version_menu.select.should(be.visible).should(be.enabled)
        versions_dialog.lumenisx_version_menu.select.should(be.visible).should(be.enabled)
        versions_dialog.publish_update_button.should(be.visible).should(be.clickable)
        versions_dialog.cancel_button.should(be.visible).should(be.clickable)

        versions_dialog.group_name_input.should(have.value(group))
        assert_that(versions_dialog.lumenisx_version_menu.get_items()).contains(valid_version)\
            .does_not_contain(invalid_version)
        versions_dialog.select_lumenisx_version(valid_version)\
            .publish_update()

        assert_that(groups_page.notification.get_message())\
            .is_equal_to(UpdateGroupVersionsDialog.VERSION_PUBLISHED_MESSAGE)

        groups_page.search_by(group)
        actual_group_version = groups_page.table.wait_to_load().get_row_by_name(group)\
            .get_cell_text(GroupsTable.Headers.LUMX_VERSION)
        assert_that(actual_group_version).is_equal_to(valid_version)


    @pytest.mark.skip(reason="Fix later ")
    @allure.title("3.6.6 Group Devices Status")
    @allure.description_html("""
    <ol>
        <li>Create a new device</li>
        <li>Select some group and update the LumenisX version</li>
        <li>Assign the device to the group</li>
        <li>In the group row click on “Status” – A “Group Devices Status” window will open</li>
        <li>Verify that:</li>
        <li>1. These titles will appear: “Group Name”, “Desired Software Version”, “Desired LumenisX Version”</li>
        <li>2. The following fields are displayed: “Serial Number”, “Device Type”, “Curr Soft Ver”, “0pdate Date”,
             “Curr LumX Ver”, “Update Date”.</li>
        <li>Verify all data in the above fields are correct</li>
        <li>Verify in “Group Devices Status” window that the “Desired LumenisX Version” field gets updated
              to the version you have published</li>
    </ol>
    """)
    @allure.severity(allure.severity_level.NORMAL)
    def test_group_device_status(self):
        test_device = random_device()

        login_as(super_admin_credentials)
        version_page = LumenisXVersionPage().open()
        version_page.filter_valid()
        version = self.get_first_version_from_table(version_page.table)

        DevicesPage().open().add_device(test_device)

        groups_page = GroupsPage().open()
        groups_page.search_by(TEST_GROUP_PREFIX)
        group = random_list_item(groups_page.table.get_column_values(GroupsTable.Headers.NAME))
        versions_dialog = groups_page.click_update_versions(group)
        versions_dialog.select_lumenisx_version(version)\
            .publish_update()
        groups_page.notification.wait_to_disappear()

        group_devices_dialog = groups_page.reload().search_by(group) \
            .click_assign_device(group)
        group_devices_dialog.select_device_by_serial_number(test_device.serial_number) \
            .click_update()
        groups_page.notification.wait_to_disappear()

        groups_page.search_by(group)
        device_status_dialog = groups_page.click_status(group)
        device_row = device_status_dialog.table.wait_to_load().get_row_by_serial_number(test_device.serial_number)

        assert_that(device_row.get_cell_text(GroupDevicesStatusTable.Headers.SERIAL_NUMBER)).described_as("Device SN")\
            .is_equal_to(test_device.serial_number)
        assert_that(device_row.get_cell_text(GroupDevicesStatusTable.Headers.DEVICE_TYPE)).described_as("Device type")\
            .is_equal_to(test_device.device)
        assert_that(device_row.get_cell_text(GroupDevicesStatusTable.Headers.CURR_SOFT_VER)).is_empty()
        assert_that(device_row.get_cell_text(GroupDevicesStatusTable.Headers.SOFT_UPDATE_DATE)).is_empty()
        assert_that(device_row.get_cell_text(GroupDevicesStatusTable.Headers.CURR_LUM_VER)).is_empty()
        assert_that(device_row.get_cell_text(GroupDevicesStatusTable.Headers.LUM_UPDATE_DATE)).is_empty()

        assert_that(device_status_dialog.get_group_name()).described_as("Group name").is_equal_to(group)
        assert_that(device_status_dialog.get_desired_lumenis_version()).described_as("Desired Lumenis version")\
            .is_equal_to(version)

    @staticmethod
    def create_group(groups_page: GroupsPage, group_name: str, device_group):
        create_dialog = groups_page.click_add_group()

        create_dialog.set_group_name(group_name) \
            .select_device(device_group) \
            .select_all_locations() \
            .click_create()
        groups_page.notification.wait_to_disappear()

    @staticmethod
    def open_random_device(groups_page: GroupsPage) -> GroupDevicesDialog:
        groups_page.search_by(TEST_GROUP_PREFIX + "group")
        device = random_list_item(groups_page.table.get_column_values(GroupsTable.Headers.NAME))
        return groups_page.click_assign_device(device)

    @staticmethod
    def get_first_version_from_table(table: LumenisXVersionTable):
        return table.wait_to_load().get_rows()[0].get_cell_text(LumenisXVersionTable.Headers.SOFT_VERSION)
