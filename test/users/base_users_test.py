import allure
from assertpy import assert_that

from src.domain.credentials import Credentials
from src.domain.user import User
from src.site.components.base_table import TableRowWrapper
from src.site.components.tables import UsersTable
from src.site.dialogs import EditUserDialog
from src.site.login_page import LoginPage
from src.site.pages import UsersPage
from test.test_data_provider import random_user, TEST_USERS_PREFIX


def login_as(credentials: Credentials):
    LoginPage().open().login_as(credentials)
    return UsersPage().open()


class BaseUsersTest:

    @allure.step
    def assert_user_row(self, row: TableRowWrapper, expected: User):
        headers = UsersTable.Headers

        if expected.phone_number[0] == '+':
            expected.phone_number = expected.phone_number[1:]

        assert_that(row.get_cell_text(headers.EMAIL)).is_equal_to(expected.email)
        assert_that(row.get_cell_text(headers.NAME)).is_equal_to(expected.name)
        assert_that(row.get_cell_text(headers.PHONE)).is_equal_to(expected.phone_number)
        assert_that(row.get_cell_text(headers.USER_GROUP)).is_equal_to(expected.user_group)
        assert_that(row.get_cell_text(headers.MANAGER)).is_equal_to(expected.manager)

    @allure.step
    def assert_user_fields(self, edit_dialog: EditUserDialog, expected: User):
        assert_that(edit_dialog.get_first_name()).is_equal_to(expected.first_name)
        assert_that(edit_dialog.get_last_name()).is_equal_to(expected.last_name)
        assert_that(edit_dialog.get_email()).is_equal_to(expected.email)
        assert_that(edit_dialog.get_phone_number()).is_equal_to(expected.phone_number)
        assert_that(edit_dialog.get_user_group()).is_equal_to(expected.user_group)
        #assert_that(edit_dialog.get_manager()).is_equal_to(expected.manager)

    @allure.step
    def create_random_user_with_device(self, users_page: UsersPage, manager: str, region: str,
                                       device_group: str) -> User:
        user = random_user()
        user.manager = manager

        create_dialog = users_page.click_add_user().set_user_fields(user)
        create_dialog.location_tree_picker.select_regions(region)
        create_dialog.device_tree_picker.select_device_groups(device_group)
        create_dialog.click_add_device()

        create_dialog.click_create()
        users_page.notification.wait_to_load()
        return user

    @allure.step
    def open_first_test_user_from_table_to_edit(self, users_page: UsersPage):
        users_page.search_by(TEST_USERS_PREFIX)

        first_test_user = users_page.table.get_column_values(UsersTable.Headers.EMAIL)[0]
        return users_page.open_edit_user_dialog(first_test_user)
