import allure
from selene.core.entity import Element
from selene.support.conditions import have, be

from src.site.components.base_table import _BaseTable


class UsersTable(_BaseTable):
    _EDIT_TEXT = "Edit"
    _VIEW_TEXT = "View"

    @allure.step
    def get_name_by_email(self, email: str) -> str:
        return self.get_user_column_value(email, self.Headers.NAME)

    @allure.step
    def get_phone_by_email(self, email: str) -> str:
        return self.get_user_column_value(email, self.Headers.PHONE)

    @allure.step
    def get_user_group_by_email(self, email: str) -> str:
        return self.get_user_column_value(email, self.Headers.USER_GROUP)

    @allure.step
    def get_manager_by_email(self, email: str) -> str:
        return self.get_user_column_value(email, self.Headers.MANAGER)

    @allure.step
    def is_user_editable(self, email: str) -> bool:
        return self._get_row_button_by_column_value(self.Headers.EMAIL, email).matching(have.exact_text(self._EDIT_TEXT))

    @allure.step
    def is_lock_icon_displayed(self, email: str) -> bool:
        return self._get_row_by_name(email).s(".anticon-lock").matching(be.visible)

    @allure.step
    def click_edit(self, email: str):
        self._get_row_button_with_name_by_column_value(self.Headers.EMAIL, email, self._EDIT_TEXT).click()

    @allure.step
    def click_view(self, email: str):
        self._get_row_button_with_name_by_column_value(self.Headers.EMAIL, email, self._VIEW_TEXT).click()

    @allure.step
    def _get_row_by_name(self, email: str) -> Element:
        return self.get_row_by_column_value(self.Headers.EMAIL, email)

    @allure.step
    def get_user_column_value(self, email: str, column) -> str:
        row = self.get_row_by_column_value(self.Headers.EMAIL, email)
        column_index = self._get_column_index(column)

        return self.get_row_cell_text_by_index(row, column_index)

    class Headers:
        NAME = "Name"
        EMAIL = "Email"
        PHONE = "Phone"
        USER_GROUP = "User Group"
        MANAGER = "Manager"
        ACTION_BUTTON = ""


class DeviceAssignmentTable(_BaseTable):
    _EDIT_TEXT = "Edit"
    _REMOVE_TEXT = "Remove"

    @allure.step
    def get_row_by_column_value(self, column_name: str, column_value: str) -> Element:
        self.wait_to_load()
        return self.table.s(".//tbody/tr[td[{0}][*/text()='{1}']]"
                            .format(self._get_column_index(column_name), column_value))

    @allure.step
    def get_rows_by_region(self, region: str) -> []:
        return self.get_rows_by_column_value(self.Headers.REGION, region)

    @allure.step
    def get_rows_by_device_types(self, device_types: str) -> []:
        return self.get_rows_by_column_value(self.Headers.DEVICE_TYPES, device_types)

    @allure.step
    def get_row_by_device_types(self, device_types: str) -> Element:
        return self.get_row_by_column_value(self.Headers.DEVICE_TYPES, device_types)

    @allure.step
    def click_edit(self, device_types: str):
        self._get_row_edit_button(device_types).click()

    @allure.step
    def click_remove(self, device_types: str):
        self._get_row_remove_button(device_types).click()

    @allure.step
    def is_row_contains_edit_button(self, row) -> bool:
        return self._is_row_contains_button_by_text(row, self._EDIT_TEXT)

    @allure.step
    def is_row_contains_remove_button(self, row) -> bool:
        return self._is_row_contains_button_by_text(row, self._REMOVE_TEXT)

    @allure.step
    def is_row_edit_button_enabled(self, device_types: str) -> bool:
        return self._get_row_edit_button(device_types).matching(be.enabled)

    @allure.step
    def is_row_remove_button_enabled(self, device_types: str) -> bool:
        return self._get_row_remove_button(device_types).matching(be.enabled)

    @allure.step
    def _get_row_edit_button(self, device_types: str):
        return self._get_row_button_with_name_by_column_value(self.Headers.DEVICE_TYPES, device_types, self._EDIT_TEXT)

    @allure.step
    def _get_row_remove_button(self, device_types: str):
        return self._get_row_button_with_name_by_column_value(self.Headers.DEVICE_TYPES, device_types, self._REMOVE_TEXT)

    class Headers:
        REGION = "Region"
        DEVICE_TYPES = "Device Types"
        ACTION_BUTTON = ""


class DevicesTable(_BaseTable):
    INACTIVE_STATUS = "Inactive"
    ACTIVE_STATUS = "Active"
    _PROPERTIES_TEXT = "Properties"

    @allure.step
    def get_row_by_serial_number(self, serial_number: str) -> Element:
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
    def is_device_editable(self, serial_number: str) -> bool:
        return self._get_row_button_by_column_value(self.Headers.SERIAL_NUMBER, serial_number).matching(
            have.exact_text(self._PROPERTIES_TEXT))

    @allure.step
    def is_row_contains_properties_button(self, row) -> bool:
        return self._is_row_contains_button_by_text(row, self._PROPERTIES_TEXT)

    @allure.step
    def is_row_properties_button_enabled(self, serial_number: str) -> bool:
        return self._get_row_properties_button(serial_number).matching(be.enabled)

    @allure.step
    def _get_row_properties_button(self, serial_number: str):
        return self._get_row_button_with_name_by_column_value(self.Headers.SERIAL_NUMBER, serial_number, self._PROPERTIES_TEXT)

    class Headers:
        SERIAL_NUMBER = "Serial Number"
        DEVICE_TYPE = "Device Type"
        STATUS = "Status"
        CLINIC_ID = "Clinic ID"
        CLINIC_NAME = "Clinic Name"
        COUNTRY = "Country"
        ACTION_BUTTON = ""
