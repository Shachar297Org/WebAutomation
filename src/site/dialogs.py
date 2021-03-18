import abc
from abc import ABC

import allure
from assertpy import assert_that
from selene.core import query
from selene.core.entity import Element
from selene.support.conditions import be, have
from selene.support.shared.jquery_style import s

from src.const import AmericasCountry
from src.domain.device import Customer, Device
from src.domain.user import User
from src.site.components.base_table import PaginationElement
from src.site.components.cascader_picker import RegionCountryCascaderPicker, DeviceTypeCascaderPicker
from src.site.components.simple_components import SelectBox, SearchInput
from src.site.components.tree_selector import LocationTreeSelector, DeviceTypesTreeSelector
from src.site.components.tables import DeviceAssignmentTable, PropertiesTable, AssignUserTable, V2CHistoryTable, \
    AlarmHistoryTable
from src.util.elements_util import clear_text_input, JS_CLICK


class _BaseDialog:
    def __init__(self):
        self.dialog = s(".ant-modal-content")
        self.title = self.dialog.s(".ant-modal-title")

        self.cancel_button = self.dialog.s("//button[span[text()='Cancel']]")
        self.close_button = self.dialog.s("button.ant-modal-close")

    @abc.abstractmethod
    def wait_to_load(self):
        """"Method should check if the dialog is loaded by some unique conditions
        (wait to some element that exists only for the particular dialog)"""

    @allure.step
    def get_element_label(self, element: Element) -> str:
        return element.s("./ancestor::*[contains(@class,'ant-row ant-form-item')]//label").get(query.text)

    @allure.step
    def get_element_error_message(self, element: Element) -> str:
        return element.s("./parent::span/following-sibling::div[@class='ant-form-explain']").get(query.text)

    @allure.step
    def close(self):
        self.close_button.click()

    @allure.step
    def click_cancel(self):
        self.cancel_button.click()


class _BaseCreateEditUserDialog(_BaseDialog):
    DEVICE_ASSIGNMENT_LABEL = "Device assignment"
    FIRST_NAME_LABEL = "First Name"
    LAST_NAME_LABEL = "Last Name"
    EMAIL_LABEL = "Email"
    PHONE_NUMBER_LABEL = "Phone Number"
    USER_GROUP_LABEL = "User Group"
    MANAGER_LABEL = "Manager"

    INVALID_EMAIL_MESSAGE = "The input is not valid E-mail!"
    FIELD_IS_REQUIRED_MESSAGE = "This field is required"

    def __init__(self):
        super().__init__()
        self.dialog = s("//*[@class='ant-modal-content'][.//div[contains(text(),'User')]]")
        self.first_name_input = self.dialog.s("#createUserForm_firstName")
        self.last_name_input = self.dialog.s("#createUserForm_lastName")
        self.email_input = self.dialog.s("#createUserForm_email")
        self.phone_number_input = self.dialog.s("#createUserForm_phone")

        self.user_group_select = SelectBox("#createUserForm_group")
        self.manager_select = SelectBox("#createUserForm_manager")

        self.location_tree_picker = LocationTreeSelector("//span[contains(@class, 'TreeSelector')]"
                                                         "[.//text()='Locations']")
        self.device_tree_picker = DeviceTypesTreeSelector("//span[contains(@class, 'TreeSelector')]"
                                                          "[.//text()='Device Types']")

        self.device_table = DeviceAssignmentTable(".ant-modal-content .ant-table-wrapper")
        self.pagination_element = PaginationElement(".ant-modal-content ul.ant-table-pagination")

        self.add_device_button = self.dialog.s(".//button[span[text()='Add']]")
        self.save_device_button = self.dialog.s(".//button[span[text()='Save']]")
        self.remove_device_button = self.dialog.s(".//button[span[text()='X']]")

    @allure.step
    def wait_to_load(self):
        self.phone_number_input.wait_until(be.visible)
        self.cancel_button.wait_until(be.clickable)
        return self

    @allure.step
    def set_user_fields(self, user: User):
        self.set_first_name(user.first_name)
        self.set_last_name(user.last_name)
        self.set_email(user.email)
        self.set_phone_number(user.phone_number)
        self.select_user_group(user.user_group)
        self.select_manager(user.manager)
        return self

    @allure.step
    def get_first_name(self) -> str:
        return self.first_name_input.get(query.value)

    @allure.step
    def set_first_name(self, text: str):
        clear_text_input(self.first_name_input).type(text)
        return self

    @allure.step
    def get_last_name(self) -> str:
        return self.last_name_input.get(query.value)

    @allure.step
    def set_last_name(self, text: str):
        clear_text_input(self.last_name_input).type(text)
        return self

    @allure.step
    def get_email(self) -> str:
        return self.email_input.get(query.value)

    @allure.step
    def set_email(self, text: str):
        clear_text_input(self.email_input).type(text)
        return self

    @allure.step
    def get_phone_number(self) -> str:
        return self.phone_number_input.get(query.value)

    @allure.step
    def set_phone_number(self, text: str):
        clear_text_input(self.phone_number_input.clear()).type(text)
        return self

    @allure.step
    def get_user_group(self) -> str:
        return self.user_group_select.get_selected_item()

    @allure.step
    def select_user_group(self, text: str):
        self.user_group_select.select_item(text)
        return self

    @allure.step
    def get_manager(self) -> str:
        return self.manager_select.get_selected_item()

    @allure.step
    def select_manager(self, text: str):
        self.manager_select.wait_to_be_enabled().select_item(text)
        return self

    @allure.step
    def click_add_device(self):
        self.add_device_button.click()
        return self

    @allure.step
    def click_save_device(self):
        self.save_device_button.click()
        return self

    @allure.step
    def _click_remove_device(self):
        self.remove_device_button.click()
        return self


class CreateUserDialog(_BaseCreateEditUserDialog):
    TITLE = "Create User"

    def __init__(self):
        super().__init__()
        self.create_button = self.dialog.s(".//button[span[text()='Create']]")

    @allure.step
    def wait_to_load(self):
        self.phone_number_input.wait_until(be.visible)
        self.create_button.wait_until(be.clickable)
        return self

    @allure.step
    def click_create(self):
        self.create_button.click()

    @allure.step
    def add_device_type_for_country(self, region: str, country: str, device_group: str):
        self.location_tree_picker.select_countries(region, country)
        self.device_tree_picker.select_device_groups(device_group)
        self.click_add_device()
        return self


class EditUserDialog(_BaseCreateEditUserDialog):
    TITLE = "Edit User"

    def __init__(self):
        super().__init__()
        self.save_button = self.dialog.s(".//button[span[text()='Save']]")
        self.reset_password_button = self.dialog.s(".//button[span[text()='Reset Password']]")
        self.update_button = self.dialog.s(".//button[span[text()='Update']]")
        self.user_disabled_switcher = self.dialog.s("button#createUserForm_locked")

    @allure.step
    def wait_to_load(self):
        self.manager_select.select.wait_until(be.visible)
        self.update_button.wait_until(be.clickable)
        return self

    @allure.step
    def click_save(self):
        self.save_button.click()

    @allure.step
    def click_update(self):
        self.update_button.click()

    @allure.step
    def click_reset_password(self):
        self.reset_password_button.click()
        return self

    @allure.step
    def is_user_disabled(self) -> bool:
        return self.user_disabled_switcher.matching(have.css_class("ant-switch-checked"))

    @allure.step
    def enable_user(self):
        if self.is_user_disabled():
            self._click_user_disabled_switcher()
        return self

    @allure.step
    def disable_user(self):
        if not self.is_user_disabled():
            self._click_user_disabled_switcher()
        return self

    @allure.step
    def _click_user_disabled_switcher(self):
        self.user_disabled_switcher.click()


class _BaseDeviceDialog(_BaseDialog, ABC):
    DEVICE_SERIAL_NUMBER_LABEL = "Device Serial Number"
    DEVICE_TYPE_LABEL = "Device Type"
    CLINIC_NAME_LABEL = "Clinic Name"
    FIRST_NAME_LABEL = "First Name"
    LAST_NAME_LABEL = "Last Name"
    EMAIL_LABEL = "Email"
    PHONE_NUMBER_LABEL = "Phone Number"
    CLINIC_ID_LABEL = "Clinic ID"
    STREET_LABEL = "Street"
    STREET_NUMBER_LABEL = "Street Number"
    CITY_LABEL = "City"
    POSTAL_ZIP_LABEL = "Postal / Zip"
    COMMENTS_LABEL = "Comments"
    REGION_COUNTRY_LABEL = "Region / Country"
    STATE_LABEL = "State"

    def __init__(self):
        super().__init__()
        self.dialog = s("//*[@class='ant-modal-content'][.//span[contains(text(), 'Device')]]")

        self.device_serial_number_input = self.dialog.s("#creatDeviceForm_deviceSerialNumber")
        self.device_type_picker = DeviceTypeCascaderPicker("//span[contains(@class, 'DeviceTypeSelector')]")

        self.clinic_name_input = self.dialog.s("#creatDeviceForm_clinicName")
        self.first_name_input = self.dialog.s("#creatDeviceForm_firstName")
        self.last_name_input = self.dialog.s("#creatDeviceForm_lastName")
        self.email_input = self.dialog.s("#creatDeviceForm_email")
        self.phone_number_input = self.dialog.s("#creatDeviceForm_phoneNumber")

        self.clinic_id_input = self.dialog.s("#creatDeviceForm_clinicId")
        self.street_input = self.dialog.s("#creatDeviceForm_street")
        self.street_number_input = self.dialog.s("#creatDeviceForm_streetNumber")
        self.city_input = self.dialog.s("#creatDeviceForm_city")
        self.postal_zip_input = self.dialog.s("#creatDeviceForm_zipCode")

        self.comments_textarea = self.dialog.s("#creatDeviceForm_comments")
        self.region_country_picker = RegionCountryCascaderPicker("//span[contains(@class, 'ant-cascader-picker')]"
                                                                 "[input[@id='creatDeviceForm_country']]")
        self.state_select = SelectBox("#creatDeviceForm_state")

    @allure.step
    def get_device_serial_number(self) -> str:
        return self.device_serial_number_input.get(query.value)

    @allure.step
    def set_device_serial_number(self, text: str):
        self.device_serial_number_input.type(text)
        return self

    @allure.step
    def get_device_type(self) -> str:
        return self.device_type_picker.get_selected_item()

    @allure.step
    def select_device_type_by_keyword(self, keyword):
        self.device_type_picker.select_item_by_keyword(keyword)
        return self

    @allure.step
    def select_device_type(self, device: Device):
        self.device_type_picker.open().select_device(device.group, device.model, device.device)

    # Customer fields

    @allure.step
    def get_clinic_name(self) -> str:
        return self.clinic_name_input.get(query.value)

    @allure.step
    def set_clinic_name(self, text: str):
        clear_text_input(self.clinic_name_input).type(text)
        return self

    @allure.step
    def get_first_name(self) -> str:
        return self.first_name_input.get(query.value)

    @allure.step
    def set_first_name(self, text: str):
        clear_text_input(self.first_name_input).type(text)
        return self

    @allure.step
    def get_last_name(self) -> str:
        return self.last_name_input.get(query.value)

    @allure.step
    def set_last_name(self, text: str):
        clear_text_input(self.last_name_input).type(text)
        return self

    @allure.step
    def get_email(self) -> str:
        return self.email_input.get(query.value)

    @allure.step
    def set_email(self, text: str):
        clear_text_input(self.email_input).type(text)
        return self

    @allure.step
    def get_phone_number(self) -> str:
        return self.phone_number_input.get(query.value)

    @allure.step
    def set_phone_number(self, text: str):
        clear_text_input(self.phone_number_input).type(text)
        return self

    @allure.step
    def get_clinic_id(self) -> str:
        return self.clinic_id_input.get(query.value)

    @allure.step
    def set_clinic_id(self, text: str):
        clear_text_input(self.clinic_id_input).type(text)
        return self

    @allure.step
    def get_street(self) -> str:
        return self.street_input.get(query.value)

    @allure.step
    def set_street(self, text: str):
        clear_text_input(self.street_input).type(text)
        return self

    @allure.step
    def get_street_number(self) -> str:
        return self.street_number_input.get(query.value)

    @allure.step
    def set_street_number(self, text: str):
        clear_text_input(self.street_number_input).type(text)
        return self

    @allure.step
    def get_city(self) -> str:
        return self.city_input.get(query.value)

    @allure.step
    def set_city(self, text: str):
        clear_text_input(self.city_input).type(text)
        return self

    @allure.step
    def get_postal_code_zip(self) -> str:
        return self.postal_zip_input.get(query.value)

    @allure.step
    def set_postal_code_zip(self, text: str):
        clear_text_input(self.postal_zip_input).type(text)
        return self

    @allure.step
    def get_country(self):
        return self.region_country_picker.get_selected_item()

    @allure.step
    def select_country_by_keyword(self, keyword):
        self.region_country_picker.select_item_by_keyword(keyword)
        return self

    @allure.step
    def get_state(self) -> str:
        return self.state_select.get_selected_item()

    @allure.step
    def select_state(self, text: str):
        self.state_select.select_item(text)
        return self

    @allure.step
    def get_comment(self) -> str:
        return self.comments_textarea.get(query.value)

    @allure.step
    def set_comment(self, text: str):
        clear_text_input(self.comments_textarea).type(text)
        return self

    @allure.step
    def set_customer_fields(self, customer: Customer):
        if customer.clinic_name:
            self.set_clinic_name(customer.clinic_name)
        if customer.first_name:
            self.set_first_name(customer.first_name)
        if customer.last_name:
            self.set_last_name(customer.last_name)
        if customer.email:
            self.set_email(customer.email)
        if customer.phone_number:
            self.set_phone_number(customer.phone_number)
        if customer.clinic_id:
            self.set_clinic_id(customer.clinic_id)
        if customer.street:
            self.set_street(customer.street)
        if customer.street_number:
            self.set_street_number(customer.street_number)

        if customer.city:
            self.set_city(customer.city)
        if customer.postal_zip:
            self.set_postal_code_zip(customer.postal_zip)
        if customer.region_country:
            self.select_country_by_keyword(customer.region_country)

        if customer.region_country == AmericasCountry.USA and customer.state:
            self.select_state(customer.state)

        if customer.comments:
            self.set_comment(customer.comments)

    @allure.step
    def assert_device_fields(self, expected: Device):
        assert_that(self.get_device_serial_number()).is_equal_to(expected.serial_number)
        assert_that(self.get_device_type()).contains("{0} / {1} / {2}".format(
            expected.group, expected.model, expected.device))

    @allure.step
    def assert_customer_fields(self, expected: Customer):
        if expected.clinic_name:
            assert_that(self.get_clinic_name()).is_equal_to(expected.clinic_name)
        if expected.first_name:
            assert_that(self.get_first_name()).is_equal_to(expected.first_name)
        if expected.last_name:
            assert_that(self.get_last_name()).is_equal_to(expected.last_name)
        if expected.email:
            assert_that(self.get_email()).is_equal_to(expected.email)
        if expected.phone_number:
            assert_that(self.get_phone_number()).is_equal_to(expected.phone_number)
        if expected.clinic_id:
            assert_that(self.get_clinic_id()).is_equal_to(expected.clinic_id)
        if expected.street:
            assert_that(self.get_street()).is_equal_to(expected.street)
        if expected.street_number:
            assert_that(self.get_street_number()).is_equal_to(expected.street_number)

        if expected.city:
            assert_that(self.get_city()).is_equal_to(expected.city)
        if expected.postal_zip:
            assert_that(self.get_postal_code_zip()).is_equal_to(expected.postal_zip)
        if expected.region_country:
            assert_that(self.get_country()).contains(expected.region_country)

        if expected.state:
            assert_that(self.get_state()).is_equal_to(expected.state)

        if expected.comments:
            assert_that(self.get_comment()).is_equal_to(expected.comments)


class CreateDeviceDialog(_BaseDeviceDialog):
    TITLE = "Create Device"

    def __init__(self):
        super().__init__()
        self.dialog = s("//*[@class='ant-modal-content'][.//span[text()='Create Device']]")
        self.create_device_button = self.dialog.s(".//button[span[text()='Create Device']]")

    @allure.step
    def wait_to_load(self):
        self.device_serial_number_input.wait_until(be.visible)
        self.comments_textarea.wait_until(be.clickable)
        return self

    @allure.step
    def click_create(self):
        self.create_device_button.click()


class DevicePropertiesDialog(_BaseDialog):
    TITLE = "Device Properties"

    def __init__(self):
        super().__init__()
        self.dialog = s("//*[@class='ant-modal-content'][.//span[text()='Device Properties']]")

        self.general = self.GeneralTab()
        self.properties = self.PropertiesTab()
        self.assign = self.AssignTab()
        self.upload_v2c = self.UploadV2CTab()
        self.v2c_history = self.V2CHistoryTab()
        self.alarms_history = self.AlarmHistoryTab()
        self.activation = self.ActivationTab()

    @allure.step
    def wait_to_load(self):
        self.dialog.wait_until(be.visible)
        self.general.wait_to_load()
        return self

    class _BaseTab(object):
        _ACTIVE_TAB_CSS = "div.ant-tabs-tabpane-active"

        def __init__(self):
            self.active_tab = s(self._ACTIVE_TAB_CSS)
            self.tabs_bar = s(".ant-tabs-left-bar")

        @property
        @abc.abstractmethod
        def name(self) -> str:
            """"Method should return the name of the tab"""

        @allure.step
        def open(self):
            return self.tabs_bar.s(".//div[@role='tab'][text()='{}']".format(self.name))

    class GeneralTab(_BaseTab, _BaseDeviceDialog):
        def __init__(self):
            super().__init__()
            _BaseDeviceDialog.__init__(self)
            self.update_customer_button = self.active_tab.s(".//button[span[text()='Update Customer']]")

        @property
        def name(self) -> str:
            return "General"

        @allure.step
        def wait_to_load(self):
            self.update_customer_button.wait_until(be.clickable)
            return self

        @allure.step
        def click_update(self):
            self.update_customer_button.click()

    class PropertiesTab(_BaseTab):
        def __init__(self):
            super().__init__()
            self.table = PropertiesTable(self._ACTIVE_TAB_CSS + " .ant-table-wrapper")

        @property
        def name(self) -> str:
            return "Properties"

    class AssignTab(_BaseTab):
        def __init__(self):
            super().__init__()
            self.search_input = SearchInput(self._ACTIVE_TAB_CSS + " input[placeholder='Search']")
            self.user_group_select = SelectBox(self._ACTIVE_TAB_CSS + " #entityToolbarFilters_userGroupFilter")
            self.reset_button = self.active_tab.s(".//button[span[text()='Reset']]")
            self.reload_button = self.active_tab.s("i.anticon-reload")
            self.table = AssignUserTable(self._ACTIVE_TAB_CSS + " .ant-table-wrapper")
            self.pagination_element = PaginationElement(self._ACTIVE_TAB_CSS + " ul.ant-table-pagination")

            self.update_user_assignment_button = self.active_tab.s(".//button[span[text()='Update User Assignment']]")

        @property
        def name(self) -> str:
            return "Assign"

        @allure.step
        def search(self, text: str):
            self.search_input.search(text)
            self.table.wait_to_load()
            return self

        @allure.step
        def filter_by_group(self, user_group: str):
            self.user_group_select.select_item(user_group)
            self.table.wait_to_load()
            return self

        @allure.step
        def click_reset(self):
            self.reset_button.click()
            self.reset_button.wait.until(have.attribute("ant-click-animating-without-extra-node").value("false"))
            return self

        @allure.step
        def reload(self):
            self.reload_button.execute_script(JS_CLICK)
            self.table.wait_to_load()

        @allure.step
        def sort_asc_by_name(self):
            self.table.sort_asc(self.table.Headers.NAME)
            return self

        @allure.step
        def sort_desc_by_name(self):
            self.table.sort_desc(self.table.Headers.NAME)
            return self

        @allure.step
        def click_update_user_assignment(self):
            self.update_user_assignment_button.click()
            return self

    class UploadV2CTab(_BaseTab):
        def __init__(self):
            super().__init__()
            self.update_device_button = self.active_tab.s(".//button[span[text()='Update Device']]")
            self.upload_button = self.active_tab.s(".//button[span[text()=' Click to upload']]")
            self.comments_textarea = self.active_tab.s("textarea#preferences_comments")

        @property
        def name(self) -> str:
            return "Upload V2C"

        @allure.step
        def click_update_device(self):
            self.update_device_button.click()
            return self

        @allure.step
        def click_upload(self):
            self.upload_button.click()
            return self

        @allure.step
        def get_comments(self):
            self.comments_textarea.get(query.text)
            return self

        @allure.step
        def set_comments(self, text: str):
            self.comments_textarea.clear().type(text)
            return self

    class V2CHistoryTab(_BaseTab):
        def __init__(self):
            super().__init__()
            self.table = V2CHistoryTable(self._ACTIVE_TAB_CSS + " .ant-table-wrapper")
            self.upload_button = self.active_tab.s(".//button[span[text()='Upload']]")

        @property
        def name(self) -> str:
            return "V2C History"

    class AlarmHistoryTab(_BaseTab):
        def __init__(self):
            super().__init__()
            self.search_input = SearchInput(self._ACTIVE_TAB_CSS + " input[placeholder='Search']")
            self.status_select = SelectBox(self._ACTIVE_TAB_CSS + " #entityToolbarFilters_alarmStateOption")
            self.reset_button = self.active_tab.s(".//button[span[text()='Reset']]")
            self.reload_button = self.active_tab.s(".ant-modal-content i.anticon-reload")
            self.table = AlarmHistoryTable(self._ACTIVE_TAB_CSS + " .ant-table-wrapper")

        @allure.step
        def search(self, text: str):
            self.search_input.search(text)
            self.table.wait_to_load()
            return self

        @allure.step
        def filter_by_status(self, status: str):
            self.status_select.select_item(status)
            self.table.wait_to_load()
            return self

        @allure.step
        def click_reset(self):
            self.reset_button.click()
            self.reset_button.wait.until(have.attribute("ant-click-animating-without-extra-node").value("false"))
            return self

        @allure.step
        def reload(self):
            self.reload_button.execute_script(JS_CLICK)
            self.table.wait_to_load()

        @property
        def name(self) -> str:
            return "Alarm History"

    class ActivationTab(_BaseTab):
        def __init__(self):
            super().__init__()
            self.status_select = SelectBox(self._ACTIVE_TAB_CSS + " #entityToolbarFilters_alarmStateOption")
            self.deactivate_device_button = self.active_tab.s(".//button[span[text()='Deactivate Device']]")
            self.reactivate_device_button = self.active_tab.s(".//button[span[text()='Reactivate Device']]")
            self.device_status = self.active_tab.s("h4.ant-typography")

        @property
        def name(self) -> str:
            return "Activation"

        @allure.step
        def click_deactivate_device(self):
            self.deactivate_device_button.click()

        @allure.step
        def click_reactivate_device(self):
            self.reactivate_device_button.click()
