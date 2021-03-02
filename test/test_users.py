import allure
import pytest
from assertpy import assert_that
from selene.support.conditions import be, have

from src.const import Feature, Region, APAC_Country, DeviceType
from src.site.components.tree_selector import SEPARATOR, get_formatted_selected_plus_item
from src.site.dialogs import CreateUserDialog
from src.site.login_page import LoginPage
from src.site.components.tables import UsersTable, DeviceAssignmentTable
from src.site.pages import UsersPage
from src.util.random_util import random_list_item
from test.test_data_provider import generate_random_user, fota_admin_credentials


@pytest.fixture(scope="class")
def login(request):
    home_page = LoginPage().open().login_as(fota_admin_credentials)
    if request.cls is not None:
        request.cls.home_page = home_page
    yield home_page


@pytest.mark.usefixtures("login")
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
    def test_user_page_elements(self):
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
    @allure.issue("wrong sorting order if the item contains more than 1 word. The second word isn't considered")
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

        for table_row in table.rows:
            assert_that(table.is_any_row_cell_contains_text_ignoring_case(table_row, random_item)).is_true()

    @allure.title("Verify that you can search in the search field by substring")
    @allure.severity(allure.severity_level.NORMAL)
    def test_filter_users_by_substring(self):
        users_page = UsersPage().open()
        table = users_page.table.wait_to_load()
        init_rows_count = len(table.rows)
        random_name = random_list_item(table.get_column_values(UsersTable.Headers.NAME))
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
        random_group = random_list_item(table.get_column_values(UsersTable.Headers.USER_GROUP))

        users_page.filter_by_group(random_group)

        assert_that(table.get_column_values(UsersTable.Headers.USER_GROUP)).contains_only(random_group)

        users_page.click_reset()

        assert_that(table.rows).described_as("Table rows count after reset").is_length(init_rows_count)

    @allure.title("Verify 'Create User' dialog web elements")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_user_dialog_elements(self):
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
        assert_that(dialog.get_element_label(dialog.phone_number_input)).is_equal_to(
            CreateUserDialog.PHONE_NUMBER_LABEL)

        dialog.user_group_select.select.should(be.visible)
        assert_that(dialog.user_group_select.is_enabled()) \
            .described_as("'User Group' select to be enabled").is_true()
        assert_that(dialog.user_group_select.is_empty()) \
            .described_as("'User Group' select to be empty").is_true()
        assert_that(dialog.get_element_label(dialog.user_group_select.select)) \
            .is_equal_to(CreateUserDialog.USER_GROUP_LABEL)

        dialog.manager_select.select.should(be.visible)
        assert_that(dialog.manager_select.is_disabled()) \
            .described_as("'Manager' select to be disabled").is_true()
        assert_that(dialog.manager_select.is_empty()) \
            .described_as("'Manager' select to be empty").is_true()
        assert_that(dialog.get_element_label(dialog.manager_select.select)) \
            .is_equal_to(CreateUserDialog.MANAGER_LABEL)

        dialog.location_tree_picker.tree_selector.should(be.visible).should(be.enabled)
        assert_that(dialog.location_tree_picker.is_enabled()) \
            .described_as("'Location' tree picker to be enabled").is_true()
        assert_that(dialog.location_tree_picker.selected_items()) \
            .described_as("'Location' tree picker to be empty").is_empty()
        assert_that(dialog.get_element_label(dialog.location_tree_picker.tree_selector)) \
            .is_equal_to(CreateUserDialog.DEVICE_ASSIGNMENT_LABEL)

        dialog.device_tree_picker.tree_selector.should(be.visible).should(be.enabled)
        assert_that(dialog.device_tree_picker.is_enabled()) \
            .described_as("'Device Types' tree picker to be enabled").is_true()
        assert_that(dialog.device_tree_picker.selected_items()) \
            .described_as("'Device Types' tree picker to be empty").is_empty()

        dialog.device_table.table.should(be.visible).should(be.enabled)
        assert_that(dialog.device_table.rows).described_as("Device table to be empty").is_empty()
        assert_that(dialog.device_table.get_headers()).contains_only(headers.REGION, headers.DEVICE_TYPES,
                                                                     headers.ACTION_BUTTON)

        dialog.add_device_button.should(be.visible).should(be.disabled)
        dialog.close_button.should(be.visible).should(be.clickable)
        dialog.create_button.should(be.visible).should(be.clickable)
        dialog.cancel_button.should(be.visible).should(be.clickable)

    @allure.title("Create a new user")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_user(self):
        headers = UsersTable.Headers
        new_user = generate_random_user()

        users_page = UsersPage().open()
        users_page.add_user(new_user)

        assert_that(users_page.get_notification_message()).is_equal_to(UsersPage.USER_CREATED_MESSAGE)

        users_page.reload().search_by(new_user.email)

        assert_that(users_page.table.get_column_values(headers.EMAIL)).contains_only(new_user.email)
        assert_that(users_page.table.get_name_by_email(new_user.email)).is_equal_to(new_user.name)
        assert_that(users_page.table.get_phone_by_email(new_user.email)).is_equal_to(new_user.phone_number)
        assert_that(users_page.table.get_user_group_by_email(new_user.email)).is_equal_to(new_user.user_group)
        assert_that(users_page.table.get_manager_by_email(new_user.email)).is_equal_to(new_user.manager)

        assert_that(users_page.table.is_user_editable(new_user.email)).described_as("Edit link").is_true()

        edit_dialog = users_page.open_edit_user_dialog(new_user.email)

        assert_that(edit_dialog.get_first_name()).is_equal_to(new_user.first_name)
        assert_that(edit_dialog.get_last_name()).is_equal_to(new_user.last_name)
        assert_that(edit_dialog.get_email()).is_equal_to(new_user.email)
        assert_that(edit_dialog.get_phone_number()).is_equal_to(new_user.phone_number)
        assert_that(edit_dialog.get_user_group()).is_equal_to(new_user.user_group)
        assert_that(edit_dialog.get_manager()).is_equal_to(new_user.manager)

    @allure.title("Create a new user with added device")
    @allure.severity(allure.severity_level.NORMAL)
    def test_add_device(self):
        test_region = Region.APAC
        test_country1 = APAC_Country.AUSTRALIA
        test_country2 = APAC_Country.INDONESIA
        test_country3 = APAC_Country.SINGAPORE
        test_countries_count = 3
        test_device_group = DeviceType.ACUPULSE
        test_device_model = "Acupulse - 30W"
        test_device1 = "GA-0000070CN"
        test_device2 = "GA-0000070DE"
        test_device3 = "GA-0000070GR"
        test_device4 = "GA-0000070"
        test_devices_count = 4

        expected_region = "{reg}/{country1}, {reg}/{country2}, {reg}/{country3}".format \
            (reg=test_region, country1=test_country1, country2=test_country2, country3=test_country3)
        expected_device_types = "{group}/{model}/{device1}, {group}/{model}/{device2}, {group}/{model}/{device3}," \
                                " {group}/{model}/{device4}".format(group=test_device_group, model=test_device_model,
                                                                    device1=test_device1, device2=test_device2,
                                                                    device3=test_device3, device4=test_device4)
        expected_device_tooltip_prefix = test_device_group + SEPARATOR + test_device_model + SEPARATOR

        users_page = UsersPage().open()
        dialog = users_page.click_add_user()
        dialog.location_tree_picker.select_countries(test_region, test_country1, test_country2, test_country3)
        dialog.device_tree_picker.select_devices(DeviceType.ACUPULSE, test_device_model,
                                                 test_device1, test_device2, test_device3, test_device4)

        assert_that(dialog.location_tree_picker.get_all_selected_items()).contains_only(
            test_region + SEPARATOR + test_country1,
            get_formatted_selected_plus_item(test_countries_count - 1)
        )
        assert_that(dialog.device_tree_picker.get_all_selected_items()).contains_only(
            test_device_group + SEPARATOR + test_device_model + SEPARATOR + test_device1,
            get_formatted_selected_plus_item(test_devices_count - 1)
        )

        dialog.click_add_device()
        assert_that(dialog.device_table.get_column_values(DeviceAssignmentTable.Headers.REGION)) \
            .contains_only(expected_region)
        assert_that(dialog.device_table.get_column_values(DeviceAssignmentTable.Headers.DEVICE_TYPES))\
            .contains_only(expected_device_types)

        for row in dialog.device_table.rows:
            assert_that(dialog.device_table.is_row_contains_edit_button(row)).described_as("Edit button").is_true()
            assert_that(dialog.device_table.is_row_contains_remove_button(row)).described_as("Remove button").is_true()

        tooltip = dialog.device_table.hover_column_cell(DeviceAssignmentTable.Headers.REGION, expected_region,
                                                        DeviceAssignmentTable.Headers.DEVICE_TYPES).wait_to_be_loaded()
        # TODO debug why tooltip isn't hovered
        # assert_that(tooltip.get_items_text()).described_as("Tooltip device type values").contains_only(
        #     expected_device_tooltip_prefix + test_device1, expected_device_tooltip_prefix + test_device2,
        #     expected_device_tooltip_prefix + test_device3, expected_device_tooltip_prefix + test_device4)

    @allure.title("Create a new user with added device")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_user_dialog_pagination(self):
        test_region = Region.APAC
        test_device_group = DeviceType.ACUPULSE

        users_page = UsersPage().open()
        dialog = users_page.click_add_user()
        for country in [APAC_Country.AUSTRALIA, APAC_Country.SINGAPORE, APAC_Country.INDONESIA, APAC_Country.MALAYSIA,
                        APAC_Country.CHINA, APAC_Country.INDIA, APAC_Country.HONG_KONG]:
            dialog.add_device_type_for_country(test_region, country, test_device_group)

        dialog.pagination_element.element.should(be.visible).should(be.enabled)
        assert_that(dialog.pagination_element.get_active_item_number()).is_equal_to(1)
        assert_that(dialog.pagination_element.get_all_page_numbers()).contains_only("1")
        dialog.pagination_element.left_arrow.should(be.visible)
        dialog.pagination_element.right_arrow.should(be.visible)
        assert_that(dialog.pagination_element.is_left_arrow_disabled()).described_as(
            "left arrow for 7 items to be disabled").is_true()
        assert_that(dialog.pagination_element.is_right_arrow_disabled()).described_as(
            "right arrow for 7 items to be disabled").is_true()

        dialog.add_device_type_for_country(test_region, APAC_Country.THAILAND, test_device_group)

        assert_that(dialog.pagination_element.get_all_page_numbers()).contains_only("1", "2")
        dialog.pagination_element.right_arrow.should(be.clickable)
        assert_that(dialog.pagination_element.is_left_arrow_disabled()).described_as(
            "left arrow for 8 items to be disabled").is_true()
        assert_that(dialog.pagination_element.is_right_arrow_disabled()).described_as(
            "right arrow for 8 items to be disabled").is_false()
