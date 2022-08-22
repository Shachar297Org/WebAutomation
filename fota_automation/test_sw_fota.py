from asyncio import wait_for
from concurrent.futures import thread
from http import server
from typing import Tuple
import allure
import pytest
from assertpy import assert_that
from selene.support.conditions import be, have

from src.const import Feature, Region, APAC_Country, DeviceGroup, AcupulseDeviceModels, Acupulse30Wdevices, \
    AmericasCountry
from src.domain.credentials import Credentials
from src.site.components.tables import GroupsTable, GroupDevicesTable, SWVersionTable, GroupDevicesStatusTable
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
import os
import subprocess
import json
import shutil
import stat
import traceback

TEST_GROUP_PREFIX = "autotests_"

#@pytest.mark.parametrize("swPath,swVersion,deviceSN,deviceType,deviceModel,swFileType,swSupportedVersion,swInstallType", 
    #                        object_test(pytest.lazy_fixture('sw_path'), pytest.lazy_fixture('sw_version'), pytest.lazy_fixture('devices_family'),
    #                        pytest.lazy_fixture('device_type'), pytest.lazy_fixture('device_model'), pytest.lazy_fixture('sw_file_type'), 
    #                        pytest.lazy_fixture('sw_supported_version'), pytest.lazy_fixture('sw_install_type'), pytest.lazy_fixture('number_of_devices')))


@pytest.fixture(autouse=True)
def cleanup_browser_session():
    yield
    clear_session_storage()
    clear_local_storage()

def login_as(credentials: Credentials):
    LoginPage().open().login_as(credentials)
    return DevicesPage().open()

def remove_readonly(func, path, _):
    "Clear the readonly bit and reattempt the removal"
    #os.chmod(path, stat.S_IWRITE)
    #func(path)
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
    os.remove(path)

def delete_files(folder):
    #folder = '/path/to/folder'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path, onerror=remove_readonly)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


@allure.feature(Feature.FW_MANAGER)
class TestSWFOTA(BaseDevicesTest):
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
    @allure.title("Test SW FOTA process")
    @allure.severity(allure.severity_level.NORMAL)
    def test_sw_fota(self, swPath="", swVersion="", deviceSN="", deviceType="", deviceModel="",
                            swFileType="", swSupportedVersion="", swInstallType="",): 

        test_device = Device(serial_number=deviceSN, model=deviceModel, device=deviceType)

        test_group_name = TEST_GROUP_PREFIX + + random_string(8) #deviceSN.split('-').pop().join('-')

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

        #time.sleep(200)

        #group_device_status_dialog = groups_page.click_status(test_group_name).wait_to_load()
        #assert_that(group_device_status_dialog.check_sw_versions()).is_equal_to(True)

    
    @allure.title("Test SW FOTA result")
    @allure.severity(allure.severity_level.NORMAL)
    def test_sw_fota_result(test_group_name = "autotests_iRVidCaY"):

        test_group_name = "autotests_iRVidCaY"
        devices_page = login_as(super_admin_credentials).wait_to_load()

        groups_page = GroupsPage().open().wait_to_load().search_by(test_group_name)
        
        group_device_status_dialog = groups_page.click_status(test_group_name).wait_to_load()
        assert_that(group_device_status_dialog.check_sw_versions()).is_equal_to(True)


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
    @allure.title("Test SW FOTA multiple times")
    @allure.severity(allure.severity_level.NORMAL)
    def test_sw_fota_multiple_times(self, swPath, swVersion, deviceSN, deviceType, deviceModel, deviceGroup,
                            swFileType, swSupportedVersion, swInstallType, times):
                            #swPath="D:/SWFOTA/2.0.78.exe", swVersion="2.0.78", deviceSN="TEST-SWFOTA-E-1", deviceType="GA-0006200LMX", deviceModel="Stellar - System",
                            #deviceGroup="M22", swFileType="ClientWPF_Tester", swSupportedVersion="*", swInstallType="FORCE", times=1): 

        #print("SW FOTA test number {0}".format(times + 1))

        # start server and client

        server_folder_path = "D:/DeviceFolders/{0}_{1}/Server/Debug_x64/".format(deviceSN, deviceType)
        
        client_orig_folder_path = "D:/DeviceFolders/{0}_{1}/Client/Debug_x64/".format(deviceSN, deviceType)
        client_folder_path = "D:/Program Files/Lumenis/ClientWPF_Tester"

        if os.path.exists(server_folder_path + 'result'):
            os.remove(server_folder_path + 'result')

        if not os.path.exists(client_folder_path):
            os.mkdir(client_folder_path)

        #print(server_folder_path)
        #print(client_orig_folder_path)

        try:

            shutil.rmtree(client_folder_path, onerror=remove_readonly, ignore_errors=False)
            shutil.copytree(client_orig_folder_path, client_folder_path)

            server = subprocess.Popen(f'{os.path.join(server_folder_path, "LumXServerHost.exe")} {times + 1}', cwd=server_folder_path)
            time.sleep(5)

            client = subprocess.Popen(f'{os.path.join(client_orig_folder_path, "ClientWPF_Tester.exe")} {times + 1}', cwd=client_orig_folder_path)
            time.sleep(5)      

            test_device = Device(serial_number=deviceSN, group=deviceGroup, model=deviceModel, device=deviceType)

            split_device_sn = deviceSN.split('-')
            split_device_sn.pop()
            #split_device_sn.append(times)

            test_group_name = TEST_GROUP_PREFIX + "-".join(split_device_sn)
            #print(test_group_name)

            devices_page = login_as(super_admin_credentials)

            devices_page.reload().search_by(deviceSN)
            self.assert_active_device_in_table(devices_page.table, test_device)

            addSWVersionPage = SwVersionPage().open()
            
            addSWVersionPage.search_by(swVersion)
            sw_is_valid = addSWVersionPage.search(swVersion, test_device).table.is_valid(swVersion)

            if not sw_is_valid:
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
            #existing_group = groups_page.search_by(test_group_name)
            #if not existing_group.table.get_column_values(GroupsTable.Headers.NAME) == test_group_name:
            #    self.create_group(groups_page, test_group_name, test_device.device)

            groups_page.reload().search_by(test_group_name)
            
            group_devices_dialog = groups_page.click_assign_device(test_group_name) #.wait_to_load()
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

            result_file_path = os.path.join(server_folder_path, "result")
            time_to_wait = 600
            time_counter = 0

            while not os.path.exists(result_file_path):
                time.sleep(1)
                time_counter += 1
                if time_counter > time_to_wait:
                    break

            if time_counter > time_to_wait:
                print("Installation takes too long - something went wrong...")

            else:
                print("Installation took {0} seconds".format(time_counter))

                # read results file, check success
                f = open(result_file_path)

                status = f.read()

                #data = json.load(f)
                #status =  data['metrics'][0]['commandStatus']

                f.close()
                     
            with open(f"./results/{test_group_name}.log", "a") as myfile:
                myfile.write(f"{times + 1}, {time_counter}, {status}\n")

            if time_counter > time_to_wait:
                assert False, f'Installation time exceeded {time_to_wait} seconds'

            if status != 'Success':
                assert False, f'Installation status is {status}'
            else:
                pass

        except Exception as ex:
            print(traceback.format_exc())

        finally:

            # kill server and client
            client.kill()
            server.kill()

            time.sleep(5)
