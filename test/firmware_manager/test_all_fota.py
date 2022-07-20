from asyncio import wait_for
from concurrent.futures import thread
import allure
import pytest
from assertpy import assert_that
from selene.support.conditions import be, have

from src.const import Feature, Region, APAC_Country, DeviceGroup, AcupulseDeviceModels, Acupulse30Wdevices, \
    AmericasCountry
from src.domain.credentials import Credentials
from src.site.components.tables import GroupsTable, GroupDevicesTable, LumenisXVersionTable, GroupDevicesStatusTable
from src.site.components.tree_selector import SEPARATOR
from src.site.dialogs import UploadLumenisXVersionDialog, UploadSWVersionDialog, get_element_label, assert_text_input_default_state, \
    assert_tree_selector_default_state, CreateGroupDialog, GroupDevicesDialog, WarningDialog, UpdateGroupVersionsDialog
from src.site.login_page import LoginPage
from src.site.pages import GroupsPage, DevicesPage, LumenisXVersionPage, SwVersionPage
from src.util.driver_util import clear_session_storage, clear_local_storage
from src.util.random_util import random_string, random_list_item
from test.devices.base_devices_test import BaseDevicesTest
from test.test_data_provider import fota_admin_credentials, random_device, super_admin_credentials,\
    random_usa_customer, random_customer
from src.domain.device import Device, Customer
from selene.core.wait import Wait
import time

TEST_GROUP_PREFIX = "autotests_"


@pytest.fixture(autouse=True)
def cleanup_browser_session():
    yield
    clear_session_storage()
    clear_local_storage()


def login_as(credentials: Credentials):
    LoginPage().open().login_as(credentials)
    return DevicesPage().open()


@allure.feature(Feature.FW_MANAGER)
class TestFOTA(BaseDevicesTest):
    table_columns_provider = [
        GroupDevicesTable.Headers.SERIAL_NUMBER,
        GroupDevicesTable.Headers.DEVICE_TYPE,
        GroupDevicesTable.Headers.CLINIC_ID,
        GroupDevicesTable.Headers.CLINIC_NAME,
        GroupDevicesTable.Headers.REGION,
        GroupDevicesTable.Headers.COUNTRY
    ]

    @staticmethod
    def create_group(groups_page: GroupsPage, group_name: str, device_group):
        create_dialog = groups_page.click_add_group()

        create_dialog.set_group_name(group_name) \
            .select_device(device_group) \
            .select_all_locations() \
            .click_create()
        groups_page.notification.wait_to_disappear()

    @allure.description_html("""
    <ol>
        <li>Upload LumenisX version package with appropriate version</li>
        <li>Create a new device with customer fields</li>
        <li>Create a new group with the device type to match the created device</li>
        <li>On the Groups page click "Assign device"</li>
        <li>Verify that group name displayed is correct</li>
        <li>Verify that the device row contains all correct data</li>
        <li>Click update - verify notification message</li>
        <li>Verify that the device is assigned to te group</li>
    </ol>
    """)
    @allure.title("Test FOTA process")
    @allure.severity(allure.severity_level.NORMAL)
    def test_fota(self, lumxPath="D:/SWFOTA/swDesiredVersionCheck3.0.0_Force_Signed.exe", lumxVersion="3.0.0", deviceSN="FOTA-TEST-0", deviceType="GA-0000180", deviceModel="Acupulse - 40W ST"): #

        test_device = Device(serial_number=deviceSN, model=deviceModel, device=deviceType)

        test_group_name = TEST_GROUP_PREFIX + random_string(8)

        devices_page = login_as(super_admin_credentials)
                
        devices_page.reload().search_by(deviceSN)
        self.assert_active_device_in_table(devices_page.table, test_device)
        
        addVersionPage = LumenisXVersionPage().open()
        lumenisVersionDialog = addVersionPage.click_add_version()
        lumenisVersionDialog.upload(lumxPath)
        lumenisVersionDialog.set_version(lumxVersion)
        lumenisVersionDialog.click_save()

        assert_that(addVersionPage.notification.get_message()) \
            .is_equal_to(UploadLumenisXVersionDialog.LUMENISX_VERSION_UPLOADED_MESSAGE)

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

        group_devices_dialog.select_device_by_serial_number(test_device.serial_number).click_update()
        
        group_devices_dialog.dialog.wait_until(be.not_.visible)
        assert_that(groups_page.notification.get_message()) \
            .is_equal_to(GroupDevicesDialog.ASSIGNED_DEVICE_TO_GROUP_MESSAGE)

        groups_page.notification.wait_to_disappear()

        versions_dialog = groups_page.click_update_versions(test_group_name)

        versions_dialog.title.should(have.exact_text(UpdateGroupVersionsDialog.TITLE))
        versions_dialog.group_name_input.should(be.visible).should(be.not_.enabled)
        versions_dialog.software_version_menu.select.should(be.visible).should(be.enabled)
        versions_dialog.lumenisx_version_menu.select.should(be.visible).should(be.enabled)
        versions_dialog.publish_update_button.should(be.visible).should(be.clickable)
        versions_dialog.cancel_button.should(be.visible).should(be.clickable)

        versions_dialog.group_name_input.should(have.value(test_group_name))
        versions_dialog.select_lumenisx_version(lumxVersion)\
            .publish_update()

        versions_dialog.dialog.wait_until(be.not_.visible)

        assert_that(groups_page.notification.get_message())\
            .is_equal_to(UpdateGroupVersionsDialog.VERSION_PUBLISHED_MESSAGE)



        group_device_status_dialog = groups_page.click_status(test_group_name).wait_to_load()
        assert_that(group_device_status_dialog.check_lumx_versions()).is_equal_to(True)


    @allure.description_html("""
    <ol>
        <li>Upload LumenisX version package with appropriate version</li>
        <li>Create a new device with customer fields</li>
        <li>Create a new group with the device type to match the created device</li>
        <li>On the Groups page click "Assign device"</li>
        <li>Verify that group name displayed is correct</li>
        <li>Verify that the device row contains all correct data</li>
        <li>Click update - verify notification message</li>
        <li>Verify that the device is assigned to te group</li>
    </ol>
    """)
    @allure.title("Test SW FOTA process")
    @allure.severity(allure.severity_level.NORMAL)
    def test_sw_fota(self, swPath="D:/SWFOTA/swDesiredVersionCheck3.0.0_Force_Signed.exe", swVersion="3.0.0", deviceSN="SW-FOTA-TEST-0", deviceType="GA-0000180", deviceModel="Acupulse - 40W ST",
                            swFileType="TESTER_APP", swSupportedVersion="*", swInstallType="Force"): 

        test_device = Device(serial_number=deviceSN, model=deviceModel, device=deviceType)

        test_group_name = TEST_GROUP_PREFIX + random_string(8)

        devices_page = login_as(super_admin_credentials)
                
        devices_page.reload().search_by(deviceSN)
        self.assert_active_device_in_table(devices_page.table, test_device)
        
        addSWVersionPage = SwVersionPage().open()
        swVersionDialog = addSWVersionPage.click_add_version()
        swVersionDialog.upload(swPath)
        swVersionDialog.set_version(swVersion)
        swVersionDialog.set_file_type(swFileType)
        swVersionDialog.set_supported_version(swSupportedVersion)
        swVersionDialog.select_device(test_device.device)
        swVersionDialog.select_install_type(swInstallType)
        swVersionDialog.click_save()

        swVersionDialog.wait_to_disappear()

        assert_that(addSWVersionPage.notification.get_message()) \
            .is_equal_to(UploadSWVersionDialog.SW_VERSION_UPLOADED_MESSAGE)

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

        group_devices_dialog.reload().select_device_by_serial_number(test_device.serial_number).click_update()
        
        group_devices_dialog.dialog.wait_until(be.not_.visible)
        assert_that(groups_page.notification.get_message()) \
            .is_equal_to(GroupDevicesDialog.ASSIGNED_DEVICE_TO_GROUP_MESSAGE)

        groups_page.notification.wait_to_disappear()

        versions_dialog = groups_page.click_update_versions(test_group_name)

        versions_dialog.title.should(have.exact_text(UpdateGroupVersionsDialog.TITLE))
        versions_dialog.group_name_input.should(be.visible).should(be.not_.enabled)
        versions_dialog.software_version_menu.select.should(be.visible).should(be.enabled)
        versions_dialog.lumenisx_version_menu.select.should(be.visible).should(be.enabled)
        versions_dialog.publish_update_button.should(be.visible).should(be.clickable)
        versions_dialog.cancel_button.should(be.visible).should(be.clickable)

        versions_dialog.group_name_input.should(have.value(test_group_name))
        versions_dialog.select_sw_version(swVersion)\
            .publish_update()

        versions_dialog.dialog.wait_until(be.not_.visible)

        assert_that(groups_page.notification.get_message())\
            .is_equal_to(UpdateGroupVersionsDialog.VERSION_PUBLISHED_MESSAGE)


        time.sleep(200)

        group_device_status_dialog = groups_page.click_status(test_group_name).wait_to_load()
        assert_that(group_device_status_dialog.check_sw_versions()).is_equal_to(True)

    
    @allure.title("Test SW FOTA result")
    @allure.severity(allure.severity_level.NORMAL)
    def test_sw_fota_result(test_group_name = "autotests_iRVidCaY"):

        test_group_name = "autotests_iRVidCaY"
        devices_page = login_as(super_admin_credentials).wait_to_load()

        groups_page = GroupsPage().open().wait_to_load().search_by(test_group_name)
        
        group_device_status_dialog = groups_page.click_status(test_group_name).wait_to_load()
        assert_that(group_device_status_dialog.check_sw_versions()).is_equal_to(True)

        

        
