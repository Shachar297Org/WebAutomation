import allure
import pytest
from assertpy import assert_that
from selene.support.conditions import be

from src.const import Feature
from src.site.login_page import LoginPage
from src.site.components.tables import UsersTable
from src.site.pages import UsersPage
from src.util.random_util import random_list_item
from test.test_data_provider import fota_admin_credentials


@pytest.fixture(scope="class")
def login(request):
    home_page = LoginPage().open().login_as(fota_admin_credentials)
    if request.cls is not None:
        request.cls.home_page = home_page
    yield home_page


@pytest.mark.usefixtures("login")
@allure.feature(Feature.USERS)
class TestUsersList:
    table_columns_provider = [
        UsersTable.Headers.NAME,
        UsersTable.Headers.EMAIL,
        UsersTable.Headers.PHONE,
        UsersTable.Headers.USER_GROUP,
        UsersTable.Headers.MANAGER,
    ]

    @allure.title("Verify Users page web elements")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_user_page_elements(self):
        users_page = self.home_page.left_panel.open_users()
        headers = UsersTable.Headers

        users_page.add_button.should(be.visible).should(be.clickable)

        users_page.search_input.input.should(be.visible).should(be.enabled).should(be.blank)
        assert_that(users_page.search_input.get_placeholder()).is_equal_to(users_page.SEARCH_TEXT)

        users_page.user_group_select.select.should(be.visible).should(be.enabled)
        assert_that(users_page.user_group_select.is_empty()).is_true()
        assert_that(users_page.user_group_select.get_placeholder()).is_equal_to(users_page.SELECT_USERS_GROUP_TEXT)

        users_page.reset_button.button.should(be.visible).should(be.clickable)
        users_page.reload_button.should(be.visible).should(be.clickable)

        users_page.table.table.should(be.visible).should(be.enabled)
        assert_that(users_page.table.get_headers()).contains_only(headers.NAME, headers.EMAIL, headers.PHONE,
                                                                  headers.USER_GROUP, headers.MANAGER,
                                                                  headers.ACTION_BUTTON)

    @pytest.mark.skip(reason="skipping until issue is resolved")
    @allure.title("Verify that you can sort the user rows by any column")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.issue("LD-388")
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
        random_item = random_list_item(table.get_column_values(column)).split()[0]

        users_page.search_by(random_item)

        assert_that(table.get_rows()).is_not_empty()

        for table_row in table.get_rows():
            assert_that(table.is_any_row_cell_contains_text_ignoring_case(table_row, random_item)).is_true()

    @allure.title("Verify that you can search in the search field by substring")
    @allure.severity(allure.severity_level.NORMAL)
    def test_filter_users_by_substring(self):
        users_page = UsersPage().open()
        table = users_page.table.wait_to_load()
        init_rows_count = len(table.get_rows())
        random_name = random_list_item(table.get_column_values(UsersTable.Headers.NAME))
        substring = random_name[1:3]

        users_page.search_by(substring)

        assert_that(table.get_rows()).is_not_empty()

        for table_row in table.get_rows():
            assert_that(table.is_any_row_cell_contains_text_ignoring_case(table_row, substring)).is_true()

        users_page.reset()

        assert_that(users_page.search_input.is_empty()).described_as("Search input to be empty after reset").is_true()
        assert_that(table.get_rows()).described_as("Table rows count after reset").is_length(init_rows_count)

    @allure.title("Verify that you can filter users by 'User Group'")
    @allure.severity(allure.severity_level.NORMAL)
    def test_filter_by_user_group(self):
        users_page = UsersPage().open()
        table = users_page.table.wait_to_load()
        init_rows_count = len(table.get_rows())
        random_group = random_list_item(table.get_column_values(UsersTable.Headers.USER_GROUP))

        users_page.filter_by_group(random_group)

        assert_that(table.get_column_values(UsersTable.Headers.USER_GROUP)).contains_only(random_group)

        users_page.reset()

        assert_that(table.get_rows()).described_as("Table rows count after reset").is_length(init_rows_count)
