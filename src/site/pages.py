import abc

import allure
from selene.api import s
from selene.core import query
from selene.support.conditions import be, have
from selene.support.shared import browser

from src.domain.device import Device, Customer
from src.domain.user import User
from src.site.components.base_table import PaginationElement
from src.site.components.page_header import PageHeader
from src.site.components.simple_components import SearchInput, SelectBox, TopRightNotification, ResetButton
from src.site.components.tables import UsersTable, DevicesTable, GroupsTable, LumenisXVersionTable
from src.site.components.tree_selector import DeviceTypesTreeSelector, LocationTreeSelector
from src.site.dialogs import CreateUserDialog, EditUserDialog, CreateDeviceDialog, DevicePropertiesDialog, \
    UploadLumenisXVersionDialog, CreateGroupDialog, EditGroupDialog
from src.util.elements_util import JS_CLICK


class _BasePage:
    def __init__(self):
        self.logo_img = s("section img")
        self.version = s("//section[contains(@class, 'Logo__Version')]")

        self.left_panel = _LeftPanel(".ant-menu.ant-menu-inline")
        self.header = PageHeader(".ant-layout-header")
        self.notification = TopRightNotification()

        self.style = s("body style")

    @abc.abstractmethod
    def open(self):
        """"Method should open the page by URL"""

    @abc.abstractmethod
    def wait_to_load(self):
        """"Method should check if the page is loaded by some unique conditions
        (wait to some element that exists only for the particular page)"""

    @allure.step
    def get_version(self) -> str:
        return self.version.get(query.text)

    @allure.step
    def get_logo_img_url(self) -> str:
        return self.logo_img.get(query.attribute("src"))

    @allure.step
    def logout(self):
        self.header.logout()


class HomePage(_BasePage):
    def __init__(self):
        super().__init__()
        self.background_image = s("//div[contains(@class, 'HomePage__BackgroundImage')]")

    @allure.step
    def open(self):
        browser.open('/home')
        self.wait_to_load()
        return self

    @allure.step
    def wait_to_load(self):
        self.background_image.wait_until(be.visible)
        return self


class UsersPage(_BasePage):
    SEARCH_TEXT = "Search"
    SELECT_USERS_GROUP_TEXT = "Select User Group..."

    USER_CREATED_MESSAGE = "Create User successful"
    USER_UPDATED_MESSAGE = "Update User successful"
    RESET_PASSWORD_MESSAGE = "Reset Password Successful"

    def __init__(self):
        super().__init__()
        self.add_button = s("//button[span[text()='+']]")
        self.search_input = SearchInput("input[placeholder='Search']")
        self.user_group_select = SelectBox("#entityToolbarFilters_userGroupFilter")
        self.reset_button = ResetButton(s("//button[span[text()='Reset']]"))
        self.reload_button = s("i.anticon-reload")
        self.table = UsersTable(".ant-table-wrapper")
        self.pagination_element = PaginationElement("ul.ant-table-pagination")

    @allure.step
    def open(self):
        browser.open('/users')
        self.wait_to_load()
        return self

    @allure.step
    def wait_to_load(self):
        self.add_button.wait_until(be.visible)
        return self

    @allure.step
    def sort_asc_by(self, column: str):
        self.table.sort_asc(column)
        return self

    @allure.step
    def sort_desc_by(self, column: str):
        self.table.sort_desc(column)
        return self

    @allure.step
    def search_by(self, text: str):
        self.search_input.search(text)
        self.table.wait_to_load()
        return self

    @allure.step
    def filter_by_group(self, user_group: str):
        self.user_group_select.select_item(user_group)
        self.table.wait_to_load()
        return self

    @allure.step
    def add_user(self, user: User):
        self.click_add_user().set_user_fields(user).click_create()
        return self

    @allure.step
    def open_edit_user_dialog(self, email) -> EditUserDialog:
        self.table.click_edit(email)
        return EditUserDialog().wait_to_load()

    @allure.step
    def click_add_user(self) -> CreateUserDialog:
        self.add_button.click()
        return CreateUserDialog().wait_to_load()

    @allure.step
    def search_and_edit_user(self, email) -> EditUserDialog:
        self.search_by(email)
        return self.open_edit_user_dialog(email)

    @allure.step
    def reset(self):
        self.reset_button.reset()
        return self

    @allure.step
    def reload(self):
        self.reload_button.execute_script(JS_CLICK)
        self.table.wait_to_load()
        return UsersPage()


class DevicesPage(_BasePage):
    SEARCH_TEXT = "Search"
    DEVICE_TYPES_TEXT = "Device Types"
    LOCATIONS_TEXT = "Locations"

    DEVICE_CREATED_MESSAGE = "Create Device successful"
    DEVICE_UPDATED_MESSAGE = "Update Device successful"
    CREATION_FAILURE_MESSAGE = "Creation Failure"

    def __init__(self):
        super().__init__()
        self.add_button = s("//button[span[text()='+']]")
        self.search_input = SearchInput("input[placeholder='Search']")
        self.device_tree_picker = DeviceTypesTreeSelector(".//span[contains(@class, 'TreeSelector')]"
                                                          "[.//text()='Device Types']")
        self.location_tree_picker = LocationTreeSelector(".//span[contains(@class, 'TreeSelector')]"
                                                         "[.//text()='Locations']")
        self.reset_button = ResetButton(s("//button[span[text()='Reset']]"))
        self.reload_button = s("i.anticon-reload")
        self.table = DevicesTable(".ant-table-wrapper")
        self.pagination_element = PaginationElement("ul.ant-table-pagination")

    @allure.step
    def open(self):
        browser.open('/devices')
        self.wait_to_load()
        return self

    @allure.step
    def wait_to_load(self):
        self.location_tree_picker.tree_selector.wait_until(be.visible)
        self.reset_button.button.wait_until(be.clickable)
        return self

    @allure.step
    def sort_asc_by(self, column: str):
        self.table.sort_asc(column)
        return self

    @allure.step
    def sort_desc_by(self, column: str):
        self.table.sort_desc(column)
        return self

    @allure.step
    def search_by(self, text: str):
        self.search_input.search(text)
        self.table.wait_to_load()
        return self

    @allure.step
    def open_device_properties(self, serial_number) -> DevicePropertiesDialog:
        self.table.click_properties(serial_number)
        return DevicePropertiesDialog().wait_to_load()

    @allure.step
    def click_add_device(self) -> CreateDeviceDialog:
        self.add_button.click()
        return CreateDeviceDialog().wait_to_load()

    @allure.step
    def add_device(self, device: Device, customer: Customer = None):
        dialog = self.click_add_device()

        dialog.set_device_serial_number(device.serial_number)

        if device.group and device.model:
            dialog.select_device_type(device)
        else:
            dialog.select_device_type_by_keyword(device.device)

        if customer:
            dialog.set_customer_fields(customer)

        dialog.click_create()
        return self

    @allure.step
    def reset(self):
        self.reset_button.reset()
        return self

    @allure.step
    def reload(self):
        self.reload_button.execute_script(JS_CLICK)
        self.table.wait_to_load()
        return DevicesPage()

    @allure.step
    def _click_add_device(self):
        self.add_button.click()
        return self


class AlarmsPage(_BasePage):
    def __init__(self):
        super().__init__()
        self.reset_button = ResetButton(s("//button[span[text()='Reset']]"))
        self.reload_button = s("i.anticon - reload")

    @allure.step
    def open(self):
        browser.open('/alarms')
        self.wait_to_load()
        return self

    @allure.step
    def wait_to_load(self):
        self.reset_button.button.wait_until(be.visible)
        return self

    @allure.step
    def reset(self):
        self.reset_button.reset()


class QlikPage(_BasePage):

    @allure.step
    def open(self):
        browser.open('/qlik')
        return self

    def wait_to_load(self):
        raise Exception("The method isn't implemented yet")


class GroupsPage(_BasePage):
    SEARCH_TEXT = "Search"
    DEVICE_TYPES_TEXT = "Device Types"
    LOCATIONS_TEXT = "Locations"

    GROUP_CREATED_MESSAGE = "Created group successful"
    GROUP_UPDATED_MESSAGE = "Updated group successful"
    CREATION_FAILURE_MESSAGE = "Creation Failure"

    def __init__(self):
        super().__init__()
        self.add_button = s("//button[span[text()='+']]")
        self.search_input = SearchInput("input[placeholder='Search']")
        self.device_tree_picker = DeviceTypesTreeSelector("//span[contains(@class, 'TreeSelector')]"
                                                          "[.//text()='Device Types']")
        self.location_tree_picker = LocationTreeSelector("//span[contains(@class, 'TreeSelector')]"
                                                         "[.//text()='Locations']")
        self.reset_button = ResetButton(s("//button[span[text()='Reset']]"))
        self.reload_button = s("i.anticon-reload")
        self.table = GroupsTable(".ant-table-wrapper")
        self.pagination_element = PaginationElement("ul.ant-table-pagination")

    @allure.step
    def open(self):
        browser.open('/groups')
        self.wait_to_load()
        return self

    @allure.step
    def wait_to_load(self):
        self.location_tree_picker.tree_selector.wait_until(be.visible)
        self.reset_button.button.wait_until(be.clickable)
        return self

    @allure.step
    def sort_asc_by(self, column: str):
        self.table.sort_asc(column)
        return self

    @allure.step
    def sort_desc_by(self, column: str):
        self.table.sort_desc(column)
        return self

    @allure.step
    def search_by(self, text: str):
        self.search_input.search(text)
        self.table.wait_to_load()
        return self

    @allure.step
    def click_add_group(self) -> CreateGroupDialog:
        self.add_button.click()
        return CreateGroupDialog().wait_to_load()

    @allure.step
    def click_edit_group(self, name) -> EditGroupDialog:
        self.table.click_edit(name)
        return EditGroupDialog().wait_to_load()

    # @allure.step
    # def click_assign_device(self, name) -> GroupDevicesDialog:
    #     self.table.click_assign_devices(name)
    #     return GroupDevicesDialog().wait_to_load() #TODO
    #
    # @allure.step
    # def click_update_versions(self, name) -> UpdateGroupVersionsDialog:
    #     self.table.click_update_versions(name)
    #     return UpdateGroupVersionsDialog().wait_to_load() #TODO
    #
    # @allure.step
    # def click_status(self, name) -> GroupDeviceStatusDialog:
    #     self.table.click_status(name)
    #     return GroupDeviceStatusDialog().wait_to_load() #TODO

    @allure.step
    def reset(self):
        self.reset_button.reset()
        return self

    @allure.step
    def reload(self):
        self.reload_button.execute_script(JS_CLICK)
        self.table.wait_to_load()
        return GroupsPage()


class LumenisXVersionPage(_BasePage):
    SEARCH_TEXT = "Search"
    VALID_TYPE_TEXT = "Valid Type"

    VALID = "Valid"
    INVALID = "Invalid"

    CREATE_LUMENIS_VERSION_MESSAGE = "Create Lumenis version successful"
    VERSION_UPDATED_MESSAGE = "Version updated successfully"

    def __init__(self):
        super().__init__()
        self.add_button = s("//button[span[text()='+']]")
        self.search_input = SearchInput("input[placeholder='Search']")
        self.valid_type_menu = SelectBox("#entityToolbarFilters_validFilter")

        self.reset_button = ResetButton(s("//button[span[text()='Reset']]"))
        self.reload_button = s("i.anticon-reload")
        self.table = LumenisXVersionTable(".ant-table-wrapper")
        self.pagination_element = PaginationElement("ul.ant-table-pagination")

    @allure.step
    def open(self):
        browser.open('/lumenisXVersions')
        self.wait_to_load()
        return self

    @allure.step
    def wait_to_load(self):
        self.valid_type_menu.select.wait_until(be.visible)
        self.reset_button.button.wait_until(be.clickable)
        return self

    @allure.step
    def sort_asc_by(self, column: str):
        self.table.sort_asc(column)
        return self

    @allure.step
    def sort_desc_by(self, column: str):
        self.table.sort_desc(column)
        return self

    @allure.step
    def click_add_version(self) -> UploadLumenisXVersionDialog:
        self.add_button.click()
        return UploadLumenisXVersionDialog().wait_to_load()

    @allure.step
    def search_by(self, text: str):
        self.search_input.search(text)
        self.table.wait_to_load()
        return self

    @allure.step
    def filter_valid(self):
        self.valid_type_menu.select_item(LumenisXVersionPage.VALID)
        return self

    @allure.step
    def filter_invalid(self):
        self.valid_type_menu.select_item(LumenisXVersionPage.INVALID)
        return self

    @allure.step
    def make_valid(self, name):
        if not self.table.is_valid:
            self.table.click_valid(name)
        return self

    @allure.step
    def make_invalid(self, name):
        if self.table.is_valid:
            self.table.click_invalid(name)
        return self

    @allure.step
    def reset(self):
        self.reset_button.reset()
        return self

    @allure.step
    def reload(self):
        self.reload_button.execute_script(JS_CLICK)
        self.table.wait_to_load()
        return LumenisXVersionPage()


class _LeftPanel(object):
    def __init__(self, locator: str):
        self.panel = s(locator)
        self.panel.wait_until(be.visible)

        self.home_section = self.panel.s("a[href='/']")
        self.users_section = self.panel.s("a[href='/users']")
        self.devices_section = self.panel.s("a[href='/devices']")
        self.alarms_section = self.panel.s("a[href='/alarms']")
        self.qlik_section = self.panel.s("a[href='/qlik']")
        self.connect_wise_section = self.panel.s("a[href='/connectWise']")
        self.event_viewer_section = self.panel.s("a[href='/eventViewer']")
        self.firmware_manager_section = self.panel.s("//div[@class='ant-menu-submenu-title']"
                                                     "[.//span[text()='Firmware Manager']]")
        self.groups_menu_item = self.panel.s("a[href='/groups']")
        self.sw_versions_menu_item = self.panel.s("a[href='/swVersions']")
        self.lumenisx_versions_menu_item = self.panel.s("a[href='/lumenisXVersions']")

    @allure.step
    def open_home(self) -> HomePage:
        self.home_section.click()
        return HomePage().wait_to_load()

    @allure.step
    def open_users(self) -> UsersPage:
        self.users_section.click()
        return UsersPage().wait_to_load()

    @allure.step
    def open_devices(self) -> DevicesPage:
        self.devices_section.click()
        return DevicesPage().wait_to_load()

    @allure.step
    def open_alarms(self) -> AlarmsPage:
        self.alarms_section.click()
        return AlarmsPage().wait_to_load()

    @allure.step
    def open_qlik(self) -> QlikPage:
        self.qlik_section.click()
        return QlikPage()

    @allure.step
    def open_groups(self) -> GroupsPage:
        self.expand_firmware_manager_section()
        self.groups_menu_item.click()
        return GroupsPage()

    @allure.step
    def open_lumenisx_versions(self) -> HomePage:
        self.expand_firmware_manager_section()
        self.lumenisx_versions_menu_item.click()
        return HomePage()

    @allure.step
    def expand_firmware_manager_section(self):
        if not self._is_firmware_manager_section_expanded():
            self.firmware_manager_section.click()
            return self.firmware_manager_section.should(have.attribute('aria-expanded', 'true'))

    @allure.step
    def _is_firmware_manager_section_expanded(self) -> bool:
        return self.firmware_manager_section.matching(have.attribute('aria-expanded', 'true'))
