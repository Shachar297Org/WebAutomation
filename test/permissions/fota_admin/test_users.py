import allure
import pytest
from assertpy import assert_that

from src.const import Feature, Region, DeviceGroup
from src.const.UserGroup import SERVICE_MANAGER, SERVICE_TECHNICIAN, TECH_SUPPORT, SERVICE_ADMIN
from src.site.components.tables import UsersTable, DeviceAssignmentTable
from src.site.login_page import LoginPage
from src.site.pages import UsersPage
from test.test_data_provider import random_user, fota_admin_credentials, super_admin_credentials, TEST_FOTA_ADMIN
from test.users.base_users_test import BaseUsersTest


@pytest.fixture(scope="class")
def login():
    LoginPage().open().login_as(fota_admin_credentials)


@pytest.mark.usefixtures("login")
@allure.feature(Feature.PERMISSIONS)
class TestFotaAdminUsersPermissions(BaseUsersTest):

    @pytest.mark.skip(reason="not an issue, by design")
    @allure.title("3.1.2.1 FOTA admin: View all users")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.issue("LD-404")
    def test_users_list(self):
        super_admin_user = super_admin_credentials.username
        users_page = UsersPage().open()
        table = users_page.table.wait_to_load()

        users_page.search_by(super_admin_user)

        assert_that(table.get_rows()).is_not_empty()

        for table_row in table.get_rows():
            assert_that(table.is_any_row_cell_contains_text_ignoring_case(table_row, super_admin_user)).is_true()

    @allure.title("3.1.2.1 FOTA admin: Create a new user")
    @allure.issue("LD-387")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_view_user(self):
        users_page = UsersPage().open()
        new_user = random_user()

        users_page.add_user(new_user)

        assert_that(users_page.notification.get_message()).is_equal_to(UsersPage.USER_CREATED_MESSAGE)

        users_page.reload().search_by(new_user.email)

        assert_that(users_page.table.get_column_values(UsersTable.Headers.EMAIL)).contains(new_user.email)
        assert_that(users_page.table.is_user_editable(new_user.email)).described_as("Edit link").is_true()

        edit_dialog = users_page.open_edit_user_dialog(new_user.email)

        self.assert_user_fields(edit_dialog, new_user)

    @allure.title("3.1.2.1 FOTA admin: Edit a user")
    @allure.severity(allure.severity_level.NORMAL)
    def test_edit_user(self):
        existing_region = Region.JAPAN
        existing_device_group = DeviceGroup.BODYCONTOURING
        new_user = random_user()
        new_device_group = DeviceGroup.CLEARLIGHT

        users_page = UsersPage().open()
        existing_user = self.create_random_user_with_device(users_page, TEST_FOTA_ADMIN,
                                                            existing_region, existing_device_group)

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
