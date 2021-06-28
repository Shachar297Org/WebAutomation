import allure
from selene import query
from selene.core.entity import Element
from selene.support.conditions import be, have
from selene.support.shared.jquery_style import s

from src.site.components.base_table import Table, TableRowWrapper
from src.util.elements_util import extract_text


class UsersTable(Table):
    _EDIT_TEXT = "Edit"
    _VIEW_TEXT = "View"

    @allure.step
    def get_row_by_email(self, email: str) -> TableRowWrapper:
        return self.get_row_by_column_value(self.Headers.EMAIL, email)

    @allure.step
    def is_user_editable(self, email: str) -> bool:
        return self.get_row_by_email(email).has_button_with_text(self._EDIT_TEXT)

    @allure.step
    def is_lock_icon_displayed(self, email: str) -> bool:
        return self.get_row_by_email(email).row.s(".anticon-lock").matching(be.visible)

    @allure.step
    def click_edit(self, email: str):
        self.get_row_by_column_value(self.Headers.EMAIL, email).click_button(self._EDIT_TEXT)

    @allure.step
    def click_view(self, email: str):
        self.get_row_by_column_value(self.Headers.EMAIL, email).click_button(self._VIEW_TEXT)

    class Headers:
        NAME = "Name"
        EMAIL = "Email"
        PHONE = "Phone"
        USER_GROUP = "User Group"
        MANAGER = "Manager"
        ACTION_BUTTON = ""


class DeviceAssignmentTable(Table):
    _EDIT_TEXT = "Edit"
    _REMOVE_TEXT = "Remove"

    @allure.step
    def get_rows_by_region(self, region: str) -> []:
        return self.get_rows_by_column_value(self.Headers.REGION, region)

    @allure.step
    def get_row_by_region(self, region: str) -> TableRowWrapper:
        return self.get_row_by_column_value(self.Headers.REGION, region)

    @allure.step
    def get_rows_by_device_types(self, device_types: str) -> []:
        return self.get_rows_by_column_value(self.Headers.DEVICE_TYPES, device_types)

    @allure.step
    def get_row_by_device_types(self, device_types: str) -> TableRowWrapper:
        return self.get_row_by_column_value(self.Headers.DEVICE_TYPES, device_types)

    @allure.step
    def click_edit(self, device_types: str):
        self._get_row_edit_button(device_types).click()

    @allure.step
    def click_remove(self, device_types: str):
        self._get_row_remove_button(device_types).click()

    @allure.step
    def is_row_contains_edit_button(self, row) -> bool:
        return row.has_button_with_text(self._EDIT_TEXT)

    @allure.step
    def is_row_contains_remove_button(self, row) -> bool:
        return row.has_button_with_text(self._REMOVE_TEXT)

    @allure.step
    def is_row_edit_button_enabled(self, device_types: str) -> bool:
        return self._get_row_edit_button(device_types).matching(be.enabled)

    @allure.step
    def is_row_remove_button_enabled(self, device_types: str) -> bool:
        return self._get_row_remove_button(device_types).matching(be.enabled)

    @allure.step
    def _get_row_edit_button(self, device_types: str) -> Element:
        return self.get_row_by_column_value(self.Headers.DEVICE_TYPES, device_types)\
            .get_button(self._EDIT_TEXT)

    @allure.step
    def _get_row_remove_button(self, device_types: str) -> Element:
        return self.get_row_by_column_value(self.Headers.DEVICE_TYPES, device_types)\
            .get_button(self._REMOVE_TEXT)

    class Headers:
        REGION = "Region"
        DEVICE_TYPES = "Device Types"
        ACTION_BUTTON = ""


class DevicesTable(Table):
    INACTIVE_STATUS = "Inactive"
    ACTIVE_STATUS = "Active"
    _PROPERTIES_TEXT = "Properties"

    @allure.step
    def get_row_by_serial_number(self, serial_number: str) -> TableRowWrapper:
        return self.get_row_by_column_value(self.Headers.SERIAL_NUMBER, serial_number)

    @allure.step
    def get_rows_by_device_type(self, device_type: str) -> []:
        return self.get_rows_by_column_value(self.Headers.DEVICE_TYPE, device_type)

    @allure.step
    def get_rows_by_status(self, status: str) -> []:
        return self.get_rows_by_column_value(self.Headers.STATUS, status)

    @allure.step
    def click_properties(self, serial_number: str):
        self._get_row_properties_button(serial_number).click()

    @allure.step
    def device_has_properties_button(self, serial_number: str) -> bool:
        return self.get_row_by_serial_number(serial_number).has_button_with_text(self._PROPERTIES_TEXT)

    @allure.step
    def is_row_contains_properties_button(self, row) -> bool:
        return row.has_button_with_text(self._PROPERTIES_TEXT)

    @allure.step
    def is_row_properties_button_enabled(self, serial_number: str) -> bool:
        return self._get_row_properties_button(serial_number).matching(be.enabled)

    @allure.step
    def _get_row_properties_button(self, serial_number: str):
        return self.get_row_by_column_value(self.Headers.SERIAL_NUMBER, serial_number)\
            .get_button(self._PROPERTIES_TEXT)

    class Headers:
        SERIAL_NUMBER = "Serial Number"
        DEVICE_TYPE = "Device Type"
        STATUS = "Status"
        CLINIC_ID = "Clinic ID"
        CLINIC_NAME = "Clinic Name"
        COUNTRY = "Country"
        ACTION_BUTTON = ""


class PropertiesTable:

    def __init__(self, locator: str):
        self.table = s(locator)
        self.table_body = self.table.s("tbody.ant-table-tbody")
        self.rows = self.table_body.ss("tr")

    @allure.step
    def wait_to_load(self):
        self.table_body.wait.until(be.visible)
        return self

    @allure.step
    def get_properties(self) -> []:
        cells = self.table_body.ss(".//tr/td[1]")
        return extract_text(cells)

    @allure.step
    def get_property_value(self, property_name: str) -> str:
        return self.table_body.s(".//tr/td[1][*[text()='{}']]/following-sibling::td".format(property_name))\
            .get(query.text)

    class Headers:
        PROPERTY = "Property"
        VALUE = "Value"

    class Property:
        DEVICE_TYPE = "Device Type"
        DEVICE_SERIAL_NUMBER = "Device Serial Number"
        STATUS = "Status"
        CREATION_TIME = "Creation Time"
        LUMENIS_APP_VERSION = "Lumenis Application Version"
        LUMENISX_PLATFORM_VERSION = "LumenisXPlatform Version"
        START_EVENT_LOCAL_TIMESTAMP = "Start Event Local Timestamp"
        START_EVENT_INTERNET_TIMESTAMP = "Start Event Internet Timestamp"
        LOCAL_TO_INTERNET_TIMESTAMP_OFFSET = "Local To Internet Timestamp Offset"
        EVENTS_DICTIONARY_VERSION = "Events Dictionary Version"
        COMMANDS_DICTIONARY_VERSION = "Commands Dictionary Version"
        ACTIVATING_USER_EMAIL = "Activating User Email"
        ACTIVATION_TYPE = "Activation Type"
        ICCID = "ICCID"
        IMEI = "IMEI"
        CUSTOM_MESSAGE = "Custom Message"


class AssignUserTable(Table):
    _CHECKBOX_CHECKED_CLASS = "ant-checkbox-checked"

    @allure.step
    def get_user_group_by_username(self, username: str) -> str:
        return self._get_row_by_username(username).get_cell_text(AssignUserTable.Headers.USER_GROUP)

    @allure.step
    def hover_row_by_username(self, username: str) -> Element:
        return self._get_row_by_username(username).row.hover()

    @allure.step
    def select_user(self, username: str):
        if not self.is_user_selected(username):
            self._click_assign_checkbox(username).wait_until(have.css_class(self._CHECKBOX_CHECKED_CLASS))

    @allure.step
    def unselect_user(self, username: str):
        if self.is_user_selected(username):
            self._click_assign_checkbox(username).wait_until(have.no.css_class(self._CHECKBOX_CHECKED_CLASS))

    @allure.step
    def is_user_selected(self, username: str) -> bool:
        return self._get_assign_checkbox_by_username(username).matching(have.css_class(self._CHECKBOX_CHECKED_CLASS))

    def _click_assign_checkbox(self, username: str) -> Element:
        return self._get_assign_checkbox_by_username(username).click()

    def _get_assign_checkbox_by_username(self, username: str) -> Element:
        return self._get_row_by_username(username).row.s("span.ant-checkbox")

    def _get_row_by_username(self, username: str) -> TableRowWrapper:
        return self.get_row_by_column_value(AssignUserTable.Headers.NAME, username)

    class Headers:
        ASSIGN = "Assign"
        NAME = "Name"
        USER_GROUP = "User Group"


class V2CHistoryTable(Table):

    class Headers:
        FILE_NAME = "File Name"
        UPLOAD_DATE = "Upload Date"
        COMMENTS = "Comments"


class AlarmHistoryTable(Table):

    class Headers:
        DATE = "Date"
        ALARM_ID = "Alarm Id"
        DESCRIPTION = "Description"
        STATUS = "Status"


class GroupsTable(Table):
    _EDIT = "Edit"
    _ASSIGN_DEVICES = "Assign Devices"
    _UPDATE_VERSIONS = "Update Versions"
    _STATUS = "STATUS"

    @allure.step
    def get_row_by_name(self, name: str) -> TableRowWrapper:
        return self.get_row_by_column_value(self.Headers.NAME, name)

    @allure.step
    def get_rows_by_device_type(self, device_type: str) -> []:
        return self.get_rows_by_column_value(self.Headers.DEVICE_TYPE, device_type)

    @allure.step
    def click_edit(self, name: str):
        self.get_row_by_name(name).get_button(self._EDIT).click()

    @allure.step
    def click_assign_devices(self, name: str):
        self.get_row_by_name(name).get_button(self._ASSIGN_DEVICES).click()

    @allure.step
    def click_update_versions(self, name: str):
        self.get_row_by_name(name).get_button(self._UPDATE_VERSIONS).click()

    @allure.step
    def click_status(self, name: str):
        self.get_row_by_name(name).get_button(self._STATUS).click()

    class Headers:
        NAME = "Name"
        DEVICE_TYPE = "Device Type"
        REGION = "Region"
        COUNTRY = "Country"
        SW_VERSION = "SW Version"
        LUMX_VERSION = "LumX Version"
        ACTION_BUTTON = ""


class LumenisXVersionTable(Table):
    _VALID = "Valid"
    _INVALID = "Invalid"

    @allure.step
    def is_valid(self, version: str) -> bool:
        return self.get_row_by_version(version).get_button(self._VALID).matching(be.disabled)

    @allure.step
    def click_valid(self, version: str):
        self.get_row_by_version(version).get_button(self._VALID).click()

    @allure.step
    def click_invalid(self, version: str):
        self.get_row_by_version(version).get_button(self._INVALID).click()

    @allure.step
    def get_row_by_version(self, name: str) -> TableRowWrapper:
        return self.get_row_by_column_value(self.Headers.SOFT_VERSION, name)

    class Headers:
        SOFT_VERSION = "Soft Version"
        UPLOAD_DATE = "Upload Date"
        UPLOADED_BY = "Uploaded By"
        VALID_INVALID_BUTTONS = ""
