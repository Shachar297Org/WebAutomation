import allure
from selene.core import query
from selene.core.entity import Element
from selene.support.conditions import be
from selene.support.shared.jquery_style import s

from src.site.components.base_table import PaginationElement
from src.site.components.simple_components import SelectBox
from src.site.components.tree_selector import _BaseTreeSelector, DeviceLocationTreeSelector, DeviceTypesTreeSelector
from src.site.components.tables import DeviceAssignmentTable


class CreateUserDialog:
    TITLE = "Create User"
    DEVICE_ASSIGNMENT_LABEL = "Device assignment"
    FIELD_IS_REQUIRED_MESSAGE = "This field is required"
    INVALID_EMAIL_MESSAGE = "The input is not valid E-mail!"

    def __init__(self):
        self.dialog = s("//*[@class='ant-modal-content'][.//text()='Create User']")
        self.title = self.dialog.s(".ant-modal-title")

        self.first_name_input = self.dialog.s("#createUserForm_firstName")
        self.last_name_input = self.dialog.s("#createUserForm_lastName")
        self.email_input = self.dialog.s("#createUserForm_email")
        self.phone_number_input = self.dialog.s("#createUserForm_phone")

        self.user_group_select = SelectBox("#createUserForm_group")
        self.manager_select = SelectBox("#createUserForm_manager")

        self.location_tree_picker = DeviceLocationTreeSelector(".//span[contains(@class, 'TreeSelector')]"
                                                               "[.//text()='Locations']")
        self.device_types_tree_picker = DeviceTypesTreeSelector(".//span[contains(@class, 'TreeSelector')]"
                                                                "[.//text()='Device Types']")

        self.device_table = DeviceAssignmentTable(".ant-modal-content .ant-table-wrapper")
        self.pagination_element = PaginationElement(".ant-modal-content ul.ant-table-pagination")

        self.add_device_button = self.dialog.s(".//button[span[text()='Add']]")
        self.remove_device_button = self.dialog.s(".//button[span[text()='X']]")
        self.cancel_button = self.dialog.s(".//button[span[text()='Cancel']]")
        self.create_button = self.dialog.s(".//button[span[text()='Create']]")
        self.close_button = self.dialog.s("button.ant-modal-close")

    def wait_to_load(self):
        self.phone_number_input.wait_until(be.visible)
        self.cancel_button.wait_until(be.clickable)
        return self

    @allure.step
    def get_element_label(self, element: Element) -> str:
        return element.s("./ancestor::*[contains(@class,'ant-row ant-form-item')]//label").get(query.text)

    @allure.step
    def get_element_error_message(self, element: Element) -> str:
        return element.s("./parent::span/following-sibling::div[@class='ant-form-explain']").get(query.text)

    @allure.step
    def set_first_name(self, text: str):
        self.first_name_input.set_value(text)
        return self

    @allure.step
    def set_last_name(self, text: str):
        self.last_name_input.set_value(text)
        return self

    @allure.step
    def set_email(self, text: str):
        self.email_input.set_value(text)
        return self

    @allure.step
    def set_phone_number(self, text: str):
        self.phone_number_input.set_value(text)
        return self

    @allure.step
    def set_phone_number(self, text: str):
        self.phone_number_input.set_value(text)
        return self

    @allure.step
    def select_user_group(self, text: str):
        self.user_group_select.select_item(text)
        return self

    @allure.step
    def select_manager(self, text: str):
        self.manager_select.select_item(text)
        return self

    @allure.step
    def close(self):
        self.close_button.click()

    @allure.step
    def click_create(self):
        self.create_button.click()

    @allure.step
    def click_cancel(self):
        self.cancel_button.click()

    @allure.step
    def _click_add_device(self):
        self.add_device_button.click()
        return self

    @allure.step
    def _click_remove_device(self):
        self.remove_device_button.click()
        return self
