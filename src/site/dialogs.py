import allure
from selene.core import query
from selene.core.entity import Element
from selene.support.conditions import be, have
from selene.support.shared.jquery_style import s

from src.domain.user import User
from src.site.components.base_table import PaginationElement
from src.site.components.simple_components import SelectBox
from src.site.components.tree_selector import DeviceLocationTreeSelector, DeviceTypesTreeSelector
from src.site.components.tables import DeviceAssignmentTable


class _BaseCreateEditUserDialog:
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
        self.dialog = s("//*[@class='ant-modal-content'][.//div[contains(text(),'User')]]")
        self.title = self.dialog.s(".ant-modal-title")

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
        self.cancel_button = self.dialog.s(".//button[span[text()='Cancel']]")
        self.close_button = self.dialog.s("button.ant-modal-close")

    def wait_to_load(self):
        self.phone_number_input.wait_until(be.visible)
        self.cancel_button.wait_until(be.clickable)
        return self

    def set_user_fields(self, user: User):
        self.set_first_name(user.first_name)
        self.set_last_name(user.last_name)
        self.set_email(user.email)
        self.set_phone_number(user.phone_number)
        self.select_user_group(user.user_group)
        self.select_manager(user.manager)
        return self

    @allure.step
    def get_element_label(self, element: Element) -> str:
        return element.s("./ancestor::*[contains(@class,'ant-row ant-form-item')]//label").get(query.text)

    @allure.step
    def get_element_error_message(self, element: Element) -> str:
        return element.s("./parent::span/following-sibling::div[@class='ant-form-explain']").get(query.text)

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
        self.phone_number_input.set_value(text)
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
    def close(self):
        self.close_button.click()

    @allure.step
    def click_cancel(self):
        self.cancel_button.click()

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
    def is_user_enabled(self) -> bool:
        return self.user_disabled_switcher.matching(have.css_class("ant-switch-checked"))

    @allure.step
    def enable_user(self):
        if not self.is_user_enabled():
            self._click_user_disabled_switcher()

    @allure.step
    def disable_user(self):
        if self.is_user_enabled():
            self._click_user_disabled_switcher()

    @allure.step
    def _click_user_disabled_switcher(self):
        self.user_disabled_switcher.click()
