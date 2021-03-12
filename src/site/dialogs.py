import abc

import allure
from selene.core import query
from selene.core.entity import Element
from selene.support.conditions import be, have
from selene.support.shared.jquery_style import s

from src.domain.device import Customer
from src.domain.user import User
from src.site.components.base_table import PaginationElement
from src.site.components.cascader_picker import RegionCountryCascaderPicker, DeviceTypeCascaderPicker
from src.site.components.simple_components import SelectBox
from src.site.components.tree_selector import DeviceLocationTreeSelector, DeviceTypesTreeSelector
from src.site.components.tables import DeviceAssignmentTable


class _BaseDialog:
    def __init__(self):
        self.dialog = s("//*[@class='ant-modal-content']")
        self.title = self.dialog.s(".ant-modal-title")

        self.cancel_button = self.dialog.s(".//button[span[text()='Cancel']]")
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

        self.location_tree_picker = DeviceLocationTreeSelector(".//span[contains(@class, 'TreeSelector')]"
                                                               "[.//text()='Locations']")
        self.device_tree_picker = DeviceTypesTreeSelector(".//span[contains(@class, 'TreeSelector')]"
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
        self.first_name_input.clear()
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
        self.first_name_input.set_value(text)
        return self

    @allure.step
    def get_last_name(self) -> str:
        return self.last_name_input.get(query.value)

    @allure.step
    def set_last_name(self, text: str):
        self.last_name_input.set_value(text)
        return self

    @allure.step
    def get_email(self) -> str:
        return self.email_input.get(query.value)

    @allure.step
    def set_email(self, text: str):
        self.email_input.set_value(text)
        return self

    @allure.step
    def get_phone_number(self) -> str:
        return self.phone_number_input.get(query.value)

    @allure.step
    def set_phone_number(self, text: str):
        self.phone_number_input.clear().set_value(text)
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
        self.device_tree_picker.select_device_types(device_group)
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


class CreateDeviceDialog(_BaseDialog):
    TITLE = "Create Device"

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
        self.dialog = s("//*[@class='ant-modal-content'][.//span[text()='Create Device']]")

        self.device_serial_number_input = self.dialog.s("#creatDeviceForm_deviceSerialNumber")
        self.device_picker = DeviceTypeCascaderPicker(".//span[contains(@class, 'DeviceTypeSelector')]")

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

        self.create_device_button = self.dialog.s(".//button[span[text()='Create Device']]")

    @allure.step
    def wait_to_load(self):
        self.device_serial_number_input.wait_until(be.visible)
        self.comments_textarea.wait_until(be.clickable)
        return self

    @allure.step
    def click_create(self):
        self.create_device_button.click()

    @allure.step
    def get_device_serial_number(self) -> str:
        return self.device_serial_number_input.get(query.value)

    @allure.step
    def set_device_serial_number(self, text: str):
        self.device_serial_number_input.set_value(text)
        return self

    @allure.step
    def select_device_type_by_keyword(self, keyword):
        self.device_picker.select_item_by_keyword(keyword)
        return self

    # Customer fields

    @allure.step
    def get_clinic_name(self) -> str:
        return self.clinic_name_input.get(query.value)

    @allure.step
    def set_clinic_name(self, text: str):
        self.clinic_name_input.set_value(text)
        return self

    @allure.step
    def get_first_name(self) -> str:
        return self.first_name_input.get(query.value)

    @allure.step
    def set_first_name(self, text: str):
        self.first_name_input.set_value(text)
        return self

    @allure.step
    def get_last_name(self) -> str:
        return self.last_name_input.get(query.value)

    @allure.step
    def set_last_name(self, text: str):
        self.last_name_input.set_value(text)
        return self

    @allure.step
    def get_email(self) -> str:
        return self.email_input.get(query.value)

    @allure.step
    def set_email(self, text: str):
        self.email_input.set_value(text)
        return self

    @allure.step
    def get_phone_number(self) -> str:
        return self.phone_number_input.get(query.value)

    @allure.step
    def set_phone_number(self, text: str):
        self.phone_number_input.clear().set_value(text)
        return self

    @allure.step
    def get_clinic_id(self) -> str:
        return self.clinic_id_input.get(query.value)

    @allure.step
    def set_clinic_id(self, text: str):
        self.clinic_id_input.set_value(text)
        return self

    @allure.step
    def get_street(self) -> str:
        return self.street_input.get(query.value)

    @allure.step
    def set_street(self, text: str):
        self.street_input.set_value(text)
        return self

    @allure.step
    def get_street_number(self) -> str:
        return self.street_number_input.get(query.value)

    @allure.step
    def set_street_number(self, text: str):
        self.street_number_input.set_value(text)
        return self

    @allure.step
    def get_city(self) -> str:
        return self.city_input.get(query.value)

    @allure.step
    def set_city(self, text: str):
        self.city_input.set_value(text)
        return self

    @allure.step
    def get_postal_code_zip(self) -> str:
        return self.postal_zip_input.get(query.value)

    @allure.step
    def set_postal_code_zip(self, text: str):
        self.postal_zip_input.set_value(text)
        return self

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
        self.comments_textarea.set_value(text)
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

        if customer.region_country == "USA" and customer.state:
            self.select_state(customer.state)

        if customer.comments:
            self.set_comment(customer.comments)


class DevicePropertiesDialog(_BaseDialog):
    TITLE = "Device Properties"

    def wait_to_load(self):
        pass
