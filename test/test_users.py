import allure
import pytest
from assertpy import assert_that
from selene.support.conditions import be, have

from src.const import Feature
from src.site.dialogs import CreateUserDialog
from src.site.login_page import LoginPage
from src.site.components.tables import UsersTable, DeviceAssignmentTable
from src.site.pages import UsersPage
from src.util.random_util import get_random_item
from test.test_data_provider import fota_admin_credentials


@pytest.fixture(scope="class")
def login_as_fota_admin(request):
    home_page = LoginPage().open().login(fota_admin_credentials.username,
                                         fota_admin_credentials.password)
    if request.cls is not None:
        request.cls.home_page = home_page
    yield home_page


@pytest.mark.usefixtures("login_as_fota_admin")
@allure.feature(Feature.USERS)
class TestUsers:
    table_columns_provider = [
        UsersTable.Headers.NAME,
        UsersTable.Headers.EMAIL,
        UsersTable.Headers.PHONE,
        UsersTable.Headers.USER_GROUP,
        UsersTable.Headers.MANAGER,
    ]

    @allure.title("Verify Users page web elements")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_page_elements(self):
        users_page = self.home_page.left_panel.open_users()
        headers = UsersTable.Headers

        users_page.add_button.should(be.visible).should(be.clickable)

        users_page.search_input.input.should(be.visible).should(be.enabled).should(be.blank)
        assert_that(users_page.search_input.get_placeholder()).is_equal_to(users_page.SEARCH_LABEL)

        users_page.user_group_select.select.should(be.visible).should(be.enabled)
        assert_that(users_page.user_group_select.is_empty()).is_true()
        assert_that(users_page.user_group_select.get_placeholder()).is_equal_to(users_page.SELECT_USERS_GROUP_LABEL)

        users_page.reset_button.should(be.visible).should(be.clickable)
        users_page.reload_button.should(be.visible).should(be.clickable)

        users_page.table.table.should(be.visible).should(be.enabled)
        assert_that(users_page.table.get_headers()).contains_only(headers.NAME, headers.EMAIL, headers.PHONE,
                                                                  headers.USER_GROUP, headers.MANAGER,
                                                                  headers.ACTION_BUTTON)

    @allure.title("Verify that you can sort the user rows by any column")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.issue("wrong sorting order if the item contains more than 1 word. The second word isn't taking into account")
    @pytest.mark.parametrize("column", table_columns_provider)
    def test_sort_users(self, column):
        users_page = UsersPage().open()
        table = users_page.table.wait_to_load()

        assert_that(table.is_column_sorted(column)).described_as("is column sorted by default").is_false()

        users_page.sort_asc_by(column)
        sorted_asc_values = table.get_column_values(column)

        assert_that(table.is_up_icon_blue(column)).described_as("is blue sort icon up displayed").is_true()
        assert_that(sorted_asc_values).is_sorted(key=str.lower)

        users_page.sort_desc_by(column)
        sorted_desc_values = table.get_column_values(column)

        assert_that(table.is_down_icon_blue(column)).described_as("is blue sort icon down displayed").is_true()
        assert_that(sorted_desc_values).is_sorted(key=str.lower, reverse=True)

    @allure.title("Verify that you can search in the search field by all fields")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("column", table_columns_provider)
    def test_filter_users_by_column_value(self, column):
        users_page = UsersPage().open()
        table = users_page.table.wait_to_load()
        random_item = get_random_item(table.get_column_values(column)).split()[0]

        users_page.search_by(random_item)

        for table_row in table.rows:
            assert_that(table.is_any_row_cell_contains_text_ignoring_case(table_row, random_item)).is_true()

    @allure.title("Verify that you can search in the search field by substring")
    @allure.severity(allure.severity_level.NORMAL)
    def test_filter_users_by_substring(self):
        users_page = UsersPage().open()
        table = users_page.table.wait_to_load()
        init_rows_count = len(table.rows)
        random_name = get_random_item(table.get_column_values(UsersTable.Headers.NAME))
        substring = random_name[1:3]

        users_page.search_by(substring)

        for table_row in table.rows:
            assert_that(table.is_any_row_cell_contains_text_ignoring_case(table_row, substring)).is_true()

        users_page.click_reset()

        assert_that(users_page.search_input.is_empty()).described_as("Search input to be empty after reset").is_true()
        assert_that(table.rows).described_as("Table rows count after reset").is_length(init_rows_count)

    @allure.title("Verify that you can filter users by 'User Group'")
    @allure.severity(allure.severity_level.NORMAL)
    def test_filter_by_user_group(self):
        users_page = UsersPage().open()
        table = users_page.table.wait_to_load()
        init_rows_count = len(table.rows)
        random_group = get_random_item(table.get_column_values(UsersTable.Headers.USER_GROUP))

        users_page.filter_by_group(random_group)

        assert_that(table.get_column_values(UsersTable.Headers.USER_GROUP)).contains_only(random_group)

        users_page.click_reset()

        assert_that(table.rows).described_as("Table rows count after reset").is_length(init_rows_count)

    @allure.title("Verify 'Create User' dialog web elements")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_dialog_elements(self):
        headers = DeviceAssignmentTable.Headers
        dialog = UsersPage().open().click_add_user()

        dialog.title.should(have.text(CreateUserDialog.TITLE))

        dialog.first_name_input.should(be.visible).should(be.enabled).should(be.blank)
        assert_that(dialog.get_element_label(dialog.first_name_input)).is_equal_to(CreateUserDialog.FIRST_NAME_LABEL)
        dialog.last_name_input.should(be.visible).should(be.enabled).should(be.blank)
        assert_that(dialog.get_element_label(dialog.last_name_input)).is_equal_to(CreateUserDialog.LAST_NAME_LABEL)
        dialog.email_input.should(be.visible).should(be.enabled).should(be.blank)
        assert_that(dialog.get_element_label(dialog.email_input)).is_equal_to(CreateUserDialog.EMAIL_LABEL)
        dialog.phone_number_input.should(be.visible).should(be.enabled).should(be.blank)
        assert_that(dialog.get_element_label(dialog.phone_number_input)).is_equal_to(CreateUserDialog.PHONE_NUMBER_LABEL)

        dialog.user_group_select.select.should(be.visible)
        assert_that(dialog.user_group_select.is_enabled())\
            .described_as("'User Group' select to be enabled").is_true()
        assert_that(dialog.user_group_select.is_empty())\
            .described_as("'User Group' select to be empty").is_true()
        assert_that(dialog.get_element_label(dialog.user_group_select.select))\
            .is_equal_to(CreateUserDialog.USER_GROUP_LABEL)

        dialog.manager_select.select.should(be.visible)
        assert_that(dialog.manager_select.is_disabled())\
            .described_as("'Manager' select to be disabled").is_true()
        assert_that(dialog.manager_select.is_empty())\
            .described_as("'Manager' select to be empty").is_true()
        assert_that(dialog.get_element_label(dialog.manager_select.select))\
            .is_equal_to(CreateUserDialog.MANAGER_LABEL)

        dialog.location_tree_picker.tree_selector.should(be.visible).should(be.enabled)
        assert_that(dialog.location_tree_picker.is_enabled())\
            .described_as("'Location' tree picker to be enabled").is_true()
        assert_that(dialog.location_tree_picker.selected_items()) \
            .described_as("'Location' tree picker to be empty").is_empty()
        assert_that(dialog.get_element_label(dialog.location_tree_picker.tree_selector)) \
            .is_equal_to(CreateUserDialog.DEVICE_ASSIGNMENT_LABEL)

        dialog.device_types_tree_picker.tree_selector.should(be.visible).should(be.enabled)
        assert_that(dialog.device_types_tree_picker.is_enabled())\
            .described_as("'Device Types' tree picker to be enabled").is_true()
        assert_that(dialog.device_types_tree_picker.selected_items()) \
            .described_as("'Device Types' tree picker to be empty").is_empty()

        dialog.device_table.table.should(be.visible).should(be.enabled)
        assert_that(dialog.device_table.rows).described_as("Device table to be empty").is_empty()
        assert_that(dialog.device_table.get_headers()).contains_only(headers.REGION, headers.DEVICE_TYPES,
                                                                     headers.ACTION_BUTTON)

        dialog.add_device_button.should(be.visible).should(be.disabled)
        dialog.close_button.should(be.visible).should(be.clickable)
        dialog.create_button.should(be.visible).should(be.clickable)
        dialog.cancel_button.should(be.visible).should(be.clickable)
