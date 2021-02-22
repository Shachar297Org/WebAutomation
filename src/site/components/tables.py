import allure
from selene.core.entity import Element
from selene.support.conditions import have, be

from src.site.components._base_table import _BaseTable


class UsersTable(_BaseTable):
    _EDIT_TEXT = "Edit"
    _VIEW_TEXT = "View"

    @allure.step
    def get_email_by_name(self, name: str) -> str:
        return self.get_user_column_value(name, self.Headers.EMAIL)

    @allure.step
    def get_phone_by_name(self, name: str) -> str:
        return self.get_user_column_value(name, self.Headers.PHONE)

    @allure.step
    def get_user_group_by_name(self, name: str) -> str:
        return self.get_user_column_value(name, self.Headers.USER_GROUP)

    @allure.step
    def get_manager_by_name(self, name: str) -> str:
        return self.get_user_column_value(name, self.Headers.MANAGER)

    @allure.step
    def is_user_editable(self, name: str) -> bool:
        return self._get_row_button_by_column_value(self.Headers.NAME, name).matching(have.text(self._EDIT_TEXT))

    @allure.step
    def is_lock_icon_displayed(self, name: str) -> bool:
        return self.get_row_by_name(name).s(".anticon-lock").matching(be.visible)

    @allure.step
    def click_edit(self, name: str):
        return self._get_row_button_with_name_by_column_value(self.Headers.NAME, name, self._EDIT_TEXT)

    @allure.step
    def click_view(self, name: str):
        return self._get_row_button_with_name_by_column_value(self.Headers.NAME, name, self._VIEW_TEXT)

    @allure.step
    def get_row_by_name(self, name: str) -> Element:
        return self.get_row_by_column_value(self.Headers.NAME, name)

    @allure.step
    def get_user_column_value(self, user_name: str, column) -> str:
        row = self.get_row_by_column_value(self.Headers.NAME, user_name)
        column_index = self._get_column_index(column)

        return self.get_row_cell_text_by_index(row, column_index)

    class Headers:
        NAME = "Name"
        EMAIL = "Email"
        PHONE = "Phone"
        USER_GROUP = "User Group"
        MANAGER = "Manager"
        ACTION_BUTTON = ""
