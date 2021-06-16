import allure
import pytest
from assertpy import assert_that

from src.const import Feature, Region, DeviceGroup
from src.const.UserGroup import SERVICE_MANAGER, SERVICE_TECHNICIAN, TECH_SUPPORT, SERVICE_ADMIN
from src.domain.credentials import Credentials
from src.domain.user import User
from src.site.components.base_table import TableRowWrapper
from src.site.components.tables import UsersTable, DeviceAssignmentTable
from src.site.login_page import LoginPage
from src.site.pages import UsersPage
from src.util.driver_util import clear_session_storage, clear_local_storage
from test.test_data_provider import random_user, fota_admin_credentials, TEST_USERS_PREFIX, super_admin_credentials


def login_as(credentials: Credentials):
    LoginPage().open().login_as(credentials)
    return UsersPage().open()


@pytest.fixture(autouse=True)
def cleanup_browser_session():
    yield
    clear_session_storage()
    clear_local_storage()


@allure.step
def create_random_user_with_device(users_page: UsersPage, region: str, device_group: str) -> User:
    user = random_user()

    create_dialog = users_page.click_add_user().set_user_fields(user)
    create_dialog.location_tree_picker.select_regions(region)
    create_dialog.device_tree_picker.select_device_groups(device_group)
    create_dialog.click_add_device()

    create_dialog.click_create()
    users_page.notification.wait_to_load()
    return user


@allure.feature(Feature.PERMISSIONS)
class TestUsersPermissions:

    @allure.title("FOTA admin: View all users")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.issue("FOTA admin can't see users with higher permissions")
    def test_view_users(self):
        super_admin_user = super_admin_credentials.username
        users_page = login_as(fota_admin_credentials)
        table = users_page.table.wait_to_load()

        users_page.search_by(super_admin_user)

        assert_that(table.get_rows()).is_not_empty()

        for table_row in table.get_rows():
            assert_that(table.is_any_row_cell_contains_text_ignoring_case(table_row, super_admin_user)).is_true()

    @allure.title("FOTA admin: Create a new user")
    @allure.issue("Some token is displayed for few secs instead of the manager in the Manager menu")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_user(self):
        users_page = login_as(fota_admin_credentials)
        headers = UsersTable.Headers
        new_user = random_user()

        users_page.add_user(new_user)

        assert_that(users_page.notification.get_message()).is_equal_to(UsersPage.USER_CREATED_MESSAGE)

        users_page.reload().search_by(new_user.email)

        assert_that(users_page.table.get_column_values(headers.EMAIL)).contains(new_user.email)
        assert_that(users_page.table.is_user_editable(new_user.email)).described_as("Edit link").is_true()

        edit_dialog = users_page.open_edit_user_dialog(new_user.email)

        assert_that(edit_dialog.get_first_name()).is_equal_to(new_user.first_name)
        assert_that(edit_dialog.get_last_name()).is_equal_to(new_user.last_name)
        assert_that(edit_dialog.get_email()).is_equal_to(new_user.email)
        assert_that(edit_dialog.get_phone_number()).is_equal_to(new_user.phone_number)
        assert_that(edit_dialog.get_user_group()).is_equal_to(new_user.user_group)
        assert_that(edit_dialog.get_manager()).is_equal_to(new_user.manager)

    @allure.title("FOTA admin: Edit a user")
    @allure.severity(allure.severity_level.NORMAL)
    def test_edit_user(self):
        existing_region = Region.JAPAN
        existing_device_group = DeviceGroup.BODYCONTOURING
        new_user = random_user()
        new_device_group = DeviceGroup.CLEARLIGHT

        users_page = login_as(fota_admin_credentials)
        existing_user = create_random_user_with_device(users_page, existing_region, existing_device_group)

        edit_dialog = users_page.reload().search_by(existing_user.email) \
            .open_edit_user_dialog(existing_user.email)

        assert_that(edit_dialog.user_group_select.get_items())\
            .contains_only(SERVICE_ADMIN, SERVICE_MANAGER, SERVICE_TECHNICIAN, TECH_SUPPORT)

        edit_dialog.set_user_fields(new_user)
        edit_dialog.device_table.click_edit(existing_device_group)
        edit_dialog.device_tree_picker.remove_selected_item(existing_device_group)
        edit_dialog.device_tree_picker.select_device_groups(new_device_group)
        edit_dialog.click_save()

        assert_that(edit_dialog.device_table.get_column_values(DeviceAssignmentTable.Headers.DEVICE_TYPES)) \
            .contains_only(new_device_group)

        edit_dialog.click_update()

        assert_that(users_page.notification.get_message()).is_equal_to(UsersPage.USER_UPDATED_MESSAGE)

        users_page.reload().search_by(new_user.email)

        assert_that(users_page.table.get_column_values(UsersTable.Headers.EMAIL)).contains_only(new_user.email)
        user_row = users_page.table.get_row_by_email(new_user.email)
        self.assert_user_row(user_row, new_user)

    @allure.step
    def assert_user_row(self, row: TableRowWrapper, expected: User):
        headers = UsersTable.Headers
        assert_that(row.get_cell_text(headers.EMAIL)).is_equal_to(expected.email)
        assert_that(row.get_cell_text(headers.NAME)).is_equal_to(expected.name)
        assert_that(row.get_cell_text(headers.PHONE)).is_equal_to(expected.phone_number)
        assert_that(row.get_cell_text(headers.USER_GROUP)).is_equal_to(expected.user_group)
        assert_that(row.get_cell_text(headers.MANAGER)).is_equal_to(expected.manager)
