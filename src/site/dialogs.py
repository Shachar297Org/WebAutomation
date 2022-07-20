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
from src.site.components.simple_components import SelectBox, SearchInput, ResetButton
from src.site.components.tables import DeviceAssignmentTable, PropertiesTable, AssignUserTable, V2CHistoryTable, \
    AlarmHistoryTable, GroupDevicesTable, GroupDevicesStatusTable
from src.site.components.tree_selector import LocationTreeSelector, DeviceTypesTreeSelector, TreeSelector
from src.util.elements_util import clear_text_input, JS_CLICK


@allure.step
def get_element_label(element: Element) -> str:
    return element.s("./ancestor::*[contains(@class,'ant-row ant-form-item')]//label").get(query.text)


@allure.step
def get_element_error_message(element: Element) -> str:
    return element.s("./parent::span/following-sibling::div[@class='ant-form-explain']").get(query.text)


@allure.step
def assert_text_input_default_state(text_input: Element, expected_label: str):
    text_input.should(be.visible).should(be.enabled).should(be.blank)
    assert_that(get_element_label(text_input)).described_as("Input label").is_equal_to(expected_label)


@allure.step
def assert_select_box_default_state(select_box: SelectBox, expected_label: str, is_enabled=True):
    select_box.select.should(be.visible)
    assert_that(select_box.is_empty()).described_as(expected_label + " select to be empty").is_true()
    assert_that(get_element_label(select_box.select)).is_equal_to(expected_label)
    if is_enabled:
        assert_that(select_box.is_enabled()).described_as(expected_label + " select to be enabled").is_true()
    else:
        assert_that(select_box.is_enabled()).described_as(expected_label + " select to be enabled").is_false()


@allure.step
def assert_tree_selector_default_state(tree_selector: TreeSelector, placeholder: str, is_enabled=True):
    tree_selector.tree_selector.should(be.visible)
    assert_that(tree_selector.selected_items()).described_as(placeholder + "tree selector to be empty").is_empty()
    assert_that(tree_selector.get_placeholder()).is_equal_to(placeholder)

    if is_enabled:
        assert_that(tree_selector.is_enabled()).described_as(placeholder + " tree selector to be enabled").is_true()
    else:
        assert_that(tree_selector.is_enabled()).described_as(placeholder + " tree selector to be enabled").is_false()


class _BaseDialog:
    FIELD_IS_REQUIRED_MESSAGE = "This field is required"

    def __init__(self):
        self.dialog = s(".ant-modal-content")
        self.title = self.dialog.s(".ant-modal-title")

        self.cancel_button = self.dialog.s("//button[span[text()='Cancel']]")
        self.close_button = self.dialog.s("button.ant-modal-close")

    def is_visible(self) -> bool:
        return self.dialog.matching(be.visible)

    @abc.abstractmethod
    def wait_to_load(self):
        """"Method should check if the dialog is loaded by some unique conditions
        (wait to some element that exists only for the particular dialog)"""

    @allure.step
    def close(self):
        self.close_button.click()

    @allure.step
    def click_cancel(self):
        self.cancel_button.click()


class _BaseCreateEditUserDialog(_BaseDialog):
    FIRST_NAME_LABEL = "First Name"
    LAST_NAME_LABEL = "Last Name"
    EMAIL_LABEL = "Email"
    PHONE_NUMBER_LABEL = "Phone Number"
    USER_GROUP_LABEL = "User Group"
    MANAGER_LABEL = "Manager"

    DEVICE_ASSIGNMENT_LABEL = "Device assignment"
    LOCATIONS_PLACEHOLDER = "Locations"
    DEVICE_TYPES_PLACEHOLDER = "Device Types"

    INVALID_EMAIL_MESSAGE = "The input is not valid E-mail!"

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
        clear_text_input(self.phone_number_input).type(text)
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

    _MAX_CHARS_ALLOWED_ERROR = "Max {} characters allowed"
    MAX_12_CHARS_ALLOWED_ERROR = _MAX_CHARS_ALLOWED_ERROR.format(12)
    MAX_32_CHARS_ALLOWED_ERROR = _MAX_CHARS_ALLOWED_ERROR.format(32)
    MAX_36_CHARS_ALLOWED_ERROR = _MAX_CHARS_ALLOWED_ERROR.format(36)
    MAX_10_CHARS_ALLOWED_ERROR = _MAX_CHARS_ALLOWED_ERROR.format(10)
    MAX_100_CHARS_ALLOWED_ERROR = _MAX_CHARS_ALLOWED_ERROR.format(100)
    MAX_256_CHARS_ALLOWED_ERROR = _MAX_CHARS_ALLOWED_ERROR.format(256)
    EMAIL_INVALID_ERROR = "The input is not valid E-mail!"

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
        return self

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
        self.comments_textarea.should(be.not_.blank)
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
    DEVICE_STATUS = "Device Status: {}"

    def __init__(self):
        super().__init__()
        self.dialog = s("//*[@class='ant-modal-content'][.//*[text()='Device Properties']]")

        self.general_tab = self.GeneralTab()
        self.properties_tab = self.PropertiesTab()
        self.assign_tab = self.AssignTab()
        self.upload_v2c_tab = self.UploadV2CTab()
        self.v2c_history_tab = self.V2CHistoryTab()
        self.alarms_history_tab = self.AlarmHistoryTab()
        self.activation_tab = self.ActivationTab()

    @allure.step
    def wait_to_load(self):
        self.dialog.wait_until(be.present)
        self.general_tab.wait_to_load()
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
            self.tabs_bar.s(".//div[@role='tab'][text()='{}']".format(self.name)).click()
            return self

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

        def get_property(self, property_name: str):
            return self.table.get_property_value(property_name)

        @property
        def name(self) -> str:
            return "Properties"

    class AssignTab(_BaseTab):
        def __init__(self):
            super().__init__()
            self.search_input = SearchInput(self._ACTIVE_TAB_CSS + " input[placeholder='Search']")
            self.user_group_select = SelectBox(self._ACTIVE_TAB_CSS + " #entityToolbarFilters_userGroupFilter")
            self.reset_button = ResetButton(self.active_tab.s(".//button[span[text()='Reset']]"))
            self.reload_button = self.active_tab.s("i.anticon-reload")
            self.table = AssignUserTable(self._ACTIVE_TAB_CSS + " .ant-table-wrapper")
            self.pagination_element = PaginationElement(self._ACTIVE_TAB_CSS + " ul.ant-table-pagination")

            self.update_user_assignment_button = self.active_tab.s(".//button[span[text()='Update User Assignment']]")

        @property
        def name(self) -> str:
            return "Assign"

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
        def reset(self):
            self.reset_button.reset()
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
            self.reset_button = ResetButton(self.active_tab.s(".//button[span[text()='Reset']]"))
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
        def reset(self):
            self.reset_button.reset()
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


class _BaseGroupDialog(_BaseDialog):
    GROUP_NAME_LABEL = "Group Name"
    DEVICE_TYPE_FAMILY_LABEL = "Device Type / Family"
    LOCATIONS_LABEL = "Locations"
    LOCATIONS_PLACEHOLDER = LOCATIONS_LABEL

    def __init__(self):
        super().__init__()
        self.group_name_input = self.dialog.s("input#createGroupForm_name")
        self.device_type_tree_selector = DeviceTypesTreeSelector(
            "//*[contains(@class, 'ant-form-item')][.//text()='Device Type / Family']//"
            "span[contains(@class, 'TreeSelector')]")
        self.locations_tree_selector = LocationTreeSelector(
            "//*[@class='ant-modal-body']//span[contains(@class, 'TreeSelector')][.//text()='Locations']")

    @allure.step
    def wait_to_load(self):
        self.group_name_input.wait_until(be.visible)
        return self

    @allure.step
    def get_group_name(self) -> str:
        return self.group_name_input.get(query.value)

    @allure.step
    def set_group_name(self, text: str):
        self.group_name_input.clear().type(text)
        return self

    @allure.step
    def select_device(self, device: str):
        self.device_type_tree_selector.open().dropdown_search(device)
        self.device_type_tree_selector.select_filtered_item(device)
        return self

    @allure.step
    def select_all_locations(self):
        self.locations_tree_selector.select_all().close()
        return self

    @allure.step
    def select_countries(self, region, *countries):
        self.locations_tree_selector.select_countries(region, *countries).close()
        return self


class CreateGroupDialog(_BaseGroupDialog):
    TITLE = "Create Group"

    def __init__(self):
        super().__init__()
        self.create_button = self.dialog.s(".//button[span[text()='Create']]")

    @allure.step
    def wait_to_load(self):
        super().wait_to_load()
        self.create_button.wait_until(be.clickable)
        return self

    @allure.step
    def click_create(self):
        self.create_button.click()


class EditGroupDialog(_BaseGroupDialog):
    TITLE = "Edit Group"

    def __init__(self):
        super().__init__()
        self.update_button = self.dialog.s(".//button[span[text()='Update']]")

    @allure.step
    def wait_to_load(self):
        super().wait_to_load()
        self.update_button.wait_until(be.clickable)
        return self

    @allure.step
    def click_update(self):
        self.update_button.click()


class UploadLumenisXVersionDialog(_BaseDialog):
    TITLE = "Upload LumenisX Version"

    LUMENISX_VERSION_UPLOADED_MESSAGE = "Create LumenisX Version successful"

    def __init__(self):
        super().__init__()
        self.upload_button = self.dialog.s(".//button[span[text()='Click To Upload']]")
        self.upload_input = self.dialog.s("input#creatLumenisXForm_upload")
        self.version_input = self.dialog.s("input#creatLumenisXForm_version")
        self.comments_textarea = self.dialog.s("textarea#creatLumenisXForm_comments")
        self.save_button = self.dialog.s(".//button[span[text()='Save']]")

    @allure.step
    def wait_to_load(self):
        self.version_input.wait_until(be.visible)
        self.save_button.wait_until(be.clickable)
        return self

    @allure.step
    def click_upload(self):
        self.upload_button.click()

    @allure.step
    def upload(self, path):
        self.upload_input.send_keys(path)

    @allure.step
    def get_version(self) -> str:
        return self.version_input.get(query.value)

    @allure.step
    def set_version(self, text: str):
        self.version_input.clear().type(text)
        return self

    @allure.step
    def get_comments(self) -> str:
        return self.comments_textarea.get(query.value)

    @allure.step
    def set_comments(self, text: str):
        self.comments_textarea.clear().type(text)
        return self

    @allure.step
    def click_save(self):
        self.save_button.click()


class UploadSWVersionDialog(_BaseDialog):
    TITLE = "Upload SW Version"
    
    SW_VERSION_UPLOADED_MESSAGE = "Create Software Version successful"

    def __init__(self):
        super().__init__()
        self.device_type_tree_selector = DeviceTypesTreeSelector(
            "//*[@class='ant-modal']//span[contains(@class, 'TreeSelector')][.//text()='Device Types']")
        self.upload_button = self.dialog.s(".//button[span[text()='Click To Upload']]")
        self.upload_input = self.dialog.s("input#creatSwVersionsForm_upload")
        self.version_input = self.dialog.s("input#creatSwVersionsForm_version")
        self.file_type = self.dialog.s("input#creatSwVersionsForm_fileType")
        self.install_type_select = SelectBox(".ant-modal-content #creatSwVersionsForm_installTypeSelector")
        self.supported_version = self.dialog.s("input#creatSwVersionsForm_supportedVersions")
        self.comments_textarea = self.dialog.s("textarea#creatSwVersionsForm_comments")
        self.save_button = self.dialog.s(".//button[span[text()='Save']]")

    @allure.step
    def wait_to_load(self):
        self.version_input.wait_until(be.visible)
        self.save_button.wait_until(be.clickable)
        return self

    @allure.step
    def wait_to_disappear(self):
        self.dialog.wait_until(be.not_.visible)
        return self

    @allure.step
    def click_upload(self):
        self.upload_button.click()

    @allure.step
    def upload(self, path):
        self.upload_input.send_keys(path)

    @allure.step
    def get_version(self) -> str:
        return self.version_input.get(query.value)

    @allure.step
    def set_version(self, text: str):
        self.version_input.clear().type(text)
        return self

    @allure.step
    def get_comments(self) -> str:
        return self.comments_textarea.get(query.value)

    @allure.step
    def set_comments(self, text: str):
        self.comments_textarea.clear().type(text)
        return self

    @allure.step
    def get_file_type(self) -> str:
        return self.file_type.get(query.value)

    @allure.step
    def set_file_type(self, text: str):
        self.file_type.clear().type(text)
        return self

    @allure.step
    def get_supported_version(self) -> str:
        return self.supported_version.get(query.value)

    @allure.step
    def set_supported_version(self, text: str):
        self.supported_version.clear().type(text)
        return self

    @allure.step
    def get_supported_version(self) -> str:
        return self.supported_version.get(query.value)

    @allure.step
    def set_supported_version(self, text: str):
        self.supported_version.clear().type(text)
        return self

    @allure.step
    def get_install_type(self) -> str:
        return self.install_type_select.get_selected_item()

    @allure.step
    def select_install_type(self, text: str):
        self.install_type_select.select_item(text)
        return self

    @allure.step
    def select_device(self, device: str):
        self.device_type_tree_selector.open().dropdown_search(device)
        self.device_type_tree_selector.select_filtered_item(device)
        return self


    @allure.step
    def click_save(self):
        self.save_button.click()


class GroupDevicesDialog(_BaseDialog):
    TITLE = "Group Devices"
    SEARCH_PLACEHOLDER = "Search"
    DEVICE_TYPES_PLACEHOLDER = "Device Types"
    LOCATIONS_PLACEHOLDER = "Locations"

    ASSIGNED_DEVICE_TO_GROUP_MESSAGE = "Assigned device(s) to group successfully"
    CONTINUE_TEXT = "Are you sure you want to continue?"
    AT_LEAST_ONE_DEVICE_ASSIGNED_MESSAGE = "At least one device is already assigned to a group"

    def __init__(self):
        super().__init__()
        self.dialog = s("//*[@class='ant-modal-content'][.//div[contains(text(),'Group Devices')]]")
        self.group_name = self.dialog.s("//*[contains(text(),'Group Name:')]/parent::div")
        self.search_input = SearchInput(".ant-modal-content input[placeholder='Search']")
        self.device_tree_picker = DeviceTypesTreeSelector(
            "//*[@class='ant-modal']//span[contains(@class, 'TreeSelector')][.//text()='Device Types']")
        self.location_tree_picker = LocationTreeSelector(
            "//*[@class='ant-modal']//span[contains(@class, 'TreeSelector')][.//text()='Locations']")

        self.reset_button = ResetButton(self.dialog.s(".//button[span[text()='Reset']]"))
        self.reload_button = self.dialog.s("i.anticon-reload")

        self.table = GroupDevicesTable(".ant-modal-content .ant-table-wrapper")
        self.pagination_element = PaginationElement(".ant-modal-content ul.ant-table-pagination")
        self.update_device_assignment_button = self.dialog.s(".//button[span[text()='Update Device Assignment']]")

    @allure.step
    def wait_to_load(self):
        self.device_tree_picker.tree_selector.wait_until(be.visible)
        self.cancel_button.wait_until(be.clickable)
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
    def reset(self):
        self.reset_button.reset()
        return self

    @allure.step
    def reload(self):
        self.reload_button.execute_script(JS_CLICK)
        self.table.wait_to_load()
        return self

    @allure.step
    def select_device_by_serial_number(self, device_serial_number):
        
        self.search_by(device_serial_number)
        self.table.select_device(device_serial_number)
        return self

    @allure.step
    def click_update(self):
        self.update_device_assignment_button.click()

    @staticmethod
    def get_expected_device_assigned_warning(device: str, group: str) -> str:
        return "Device {0} is already assigned to group {1}".format(device, group)


class UpdateGroupVersionsDialog(_BaseDialog):
    TITLE = "Update Group Versions"
    GROUP_NAME_LABEL = "Group Name"
    SOFTWARE_VERSION_LABEL = "Software Version"
    LUMENISX_VERSION_LABEL = "LumenisX Version"

    VERSION_PUBLISHED_MESSAGE = "Version published to group successfully"

    def __init__(self):
        super().__init__()
        self.dialog = s("//*[@class='ant-modal-content'][.//div[contains(text(),'Update Group Versions')]]")
        self.group_name_input = self.dialog.s("input#updateGroupVersionForm_groupName")
        self.software_version_menu = SelectBox("#updateGroupVersionForm_softwareVersion")
        self.lumenisx_version_menu = SelectBox("#updateGroupVersionForm_lumenisXVersion")

        self.publish_update_button = self.dialog.s(".//button[span[text()='Publish Update']]")

    @allure.step
    def wait_to_load(self):
        self.publish_update_button.should(be.visible)
        return self

    @allure.step
    def wait_to_disapear(self):
        self.publish_update_button.should(be.not_.visible)
        return self

    @allure.step
    def get_group_name(self):
        return self.group_name_input.get(query.value)

    @allure.step
    def select_lumenisx_version(self, version):
        self.lumenisx_version_menu.select_item(version)
        return self
    
    @allure.step
    def select_sw_version(self, version):
        self.software_version_menu.select_item(version)
        return self

    @allure.step
    def publish_update(self):
        self.publish_update_button.click()


class GroupDevicesStatusDialog(_BaseDialog):
    TITLE = "Group Devices Status"
    GROUP_NAME_LABEL = "Group Name"
    DESIRED_SW_VERSION_LABEL = "Desired Software Version"
    DESIRED_LUMENIS_VERSION_LABEL = "Desired LumenisX Version"

    ASSIGNED_DEVICE_TO_GROUP_MESSAGE = "Assigned device(s) to group successfully"

    def __init__(self):
        super().__init__()
        self.dialog = s("//*[@class='ant-modal-content'][.//div[contains(text(),'Group Devices')]]")
        self.group_name = self.dialog.s(".//span[.//*[contains(text(),'Group Name')]]//span[2]")
        self.desired_sw_version = self.dialog.s(".//span[.//*[contains(text(),'Desired Software Version')]]//span[2]")
        self.desired_lumenis_version = self.dialog.s(
            ".//span[.//*[contains(text(),'Desired LumenisX Version')]]//span[2]")

        self.table = GroupDevicesTable(".ant-modal-content .ant-table-wrapper")
        self.pagination_element = PaginationElement(".ant-modal-content ul.ant-table-pagination")

    @allure.step
    def wait_to_load(self):
        self.dialog.wait_until(be.visible)
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
    def get_group_name(self):
        return self.group_name.get(query.text)

    @allure.step
    def get_desired_lumenis_version(self):
        return self.desired_lumenis_version.get(query.text)

    @allure.step
    def get_devices(self):
        return self.table.get_column_values(GroupDevicesStatusTable.Headers.SERIAL_NUMBER)

    @allure.step
    def check_sw_versions(self):
        sw_col_values = self.table.get_column_values(GroupDevicesStatusTable.Headers.CURR_SOFT_VER)
        result = len(set(sw_col_values)) == 1 and sw_col_values[0] == self.desired_sw_version.text

        return result

    @allure.step
    def check_lumx_versions(self):
        lumx_col_values = self.table.get_column_values(GroupDevicesStatusTable.Headers.CURR_LUM_VER)
        result = len(set(lumx_col_values)) == 1 and lumx_col_values[0] == self.desired_lumenis_version.text
        
        return result



class WarningDialog(_BaseDialog):

    def __init__(self):
        super().__init__()
        self.dialog = s("//*[@class='ant-modal-content'][.//div[contains(text(),'Warning')]]")
        self.text = self.dialog.s(".//div[contains(@class, 'WarningModal__BodyText')]")
        self.additional_text = self.dialog.s(".//div[contains(@class, 'WarningModal__BodyText')][2]")
        self.ok_button = self.dialog.s(".//button[span[text()='OK']]")

    @allure.step
    def get_text(self) -> str:
        return self.text.get(query.text)

    @allure.step
    def get_additional_text(self) -> str:
        return self.additional_text.get(query.text)

    @allure.step
    def click_ok(self):
        self.ok_button.click()

    @allure.step
    def wait_to_load(self):
        self.dialog.should(be.visible, 10)
        return self
