import allure
import pytest
from assertpy import assert_that
from selene.support.conditions import be, have

from src.const import Feature, Region, APAC_Country, DeviceType, UserGroup
from src.domain.credentials import Credentials
from src.domain.user import User
from src.site.components.tree_selector import SEPARATOR, get_formatted_selected_plus_item
from src.site.dialogs import CreateUserDialog
from src.site.login_page import LoginPage
from src.site.components.tables import UsersTable, DeviceAssignmentTable
from src.site.pages import UsersPage
from src.util.driver_util import clear_session_storage, clear_local_storage
from test.test_data_provider import generate_random_user, fota_admin_credentials, TEST_USERS_PREFIX, TEST_SUPER_ADMIN, \
    TEST_FOTA_ADMIN, TEST_SYSTEM_ENGINEER, TEST_SERVICE_ADMIN, TEST_TECH_SUPPORT, super_admin_credentials, \
    user_for_disabling_credentials


def login_as(credentials: Credentials):
    LoginPage().open().login_as(credentials)
    return UsersPage().open()


@pytest.fixture(autouse=True)
def cleanup_browser_session():
    yield
    clear_session_storage()
    clear_local_storage()


@allure.step
def create_random_user_with_device(users_page: UsersPage, region: str, device_type: str) -> User:
    user = generate_random_user()

    create_dialog = users_page.click_add_user().set_user_fields(user)
    create_dialog.location_tree_picker.select_regions(region)
    create_dialog.device_tree_picker.select_device_types(device_type)
    create_dialog.click_add_device()

    create_dialog.click_create()
    users_page.notification.wait_to_load()
    return user


def open_first_test_user_from_table_to_edit(users_page: UsersPage):
    users_page.search_by(TEST_USERS_PREFIX)

    first_test_user = users_page.table.get_column_values(UsersTable.Headers.EMAIL)[0]
    return users_page.open_edit_user_dialog(first_test_user)


@allure.feature(Feature.USERS)
class TestCreateEditUsers:

    @allure.title("Verify 'Create User' dialog web elements")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_user_dialog_elements(self):
        users_page = login_as(fota_admin_credentials)
        headers = DeviceAssignmentTable.Headers
        dialog = users_page.click_add_user()

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
    @allure.issue("Some token is displayed for few secs instead of the manager in the Manager menu")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_user(self):
        users_page = login_as(fota_admin_credentials)
        headers = UsersTable.Headers
        new_user = generate_random_user()

        users_page.add_user(new_user)

        assert_that(users_page.notification.get_message()).is_equal_to(UsersPage.USER_CREATED_MESSAGE)

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

    @allure.title("Create a new user: add devices")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_user_add_devices(self):
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

        expected_region = "{reg}/{country1}, {reg}/{country2}, {reg}/{country3}".format(
            reg=test_region, country1=test_country1, country2=test_country2, country3=test_country3)
        expected_device_types = "{group}/{model}/{device1}, {group}/{model}/{device2}, {group}/{model}/{device3}," \
                                " {group}/{model}/{device4}".format(group=test_device_group, model=test_device_model,
                                                                    device1=test_device1, device2=test_device2,
                                                                    device3=test_device3, device4=test_device4)
        expected_device_tooltip_prefix = test_device_group + SEPARATOR + test_device_model + SEPARATOR

        users_page = login_as(fota_admin_credentials)
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
        assert_that(dialog.device_table.get_column_values(DeviceAssignmentTable.Headers.DEVICE_TYPES)) \
            .contains_only(expected_device_types)

        for row in dialog.device_table.rows:
            assert_that(dialog.device_table.is_row_contains_edit_button(row)).described_as("Edit button").is_true()
            assert_that(dialog.device_table.is_row_contains_remove_button(row)).described_as("Remove button").is_true()

        # tooltip = dialog.device_table.hover_column_cell(DeviceAssignmentTable.Headers.REGION, expected_region,
        #                                                 DeviceAssignmentTable.Headers.DEVICE_TYPES).wait_to_be_loaded()
        # TODO debug why tooltip isn't hovered
        # assert_that(tooltip.get_items_text()).described_as("Tooltip device type values").contains_only(
        #     expected_device_tooltip_prefix + test_device1, expected_device_tooltip_prefix + test_device2,
        #     expected_device_tooltip_prefix + test_device3, expected_device_tooltip_prefix + test_device4)

    @allure.title("Edit a user")
    @allure.severity(allure.severity_level.NORMAL)
    def test_edit_user(self):
        existing_region = Region.JAPAN
        existing_device_type = DeviceType.BODYCONTOURING
        new_user = generate_random_user()
        new_device_type = DeviceType.CLEARLIGHT

        users_page = login_as(fota_admin_credentials)
        existing_user = create_random_user_with_device(users_page, existing_region, existing_device_type)

        edit_dialog = users_page.reload().search_by(existing_user.email) \
            .open_edit_user_dialog(existing_user.email)

        edit_dialog.set_user_fields(new_user)
        edit_dialog.device_table.click_edit(existing_device_type)
        edit_dialog.add_device_button.should(be.not_.visible)
        edit_dialog.save_button.should(be.visible).should(be.clickable)
        edit_dialog.remove_device_button.should(be.visible).should(be.clickable)

        assert_that(edit_dialog.location_tree_picker.get_all_selected_items()).contains_only(existing_region)
        assert_that(edit_dialog.device_tree_picker.get_all_selected_items()).contains_only(existing_device_type)
        existing_device_row = edit_dialog.device_table.get_row_by_device_types(existing_device_type)
        assert_that(edit_dialog.device_table.is_row_selected(existing_device_row)) \
            .described_as("Edited row to be selected(grayed)").is_true()
        assert_that(edit_dialog.device_table.is_row_edit_button_enabled(existing_device_row)) \
            .described_as("Edited row 'Edit' button to be enabled").is_false()
        assert_that(edit_dialog.device_table.is_row_remove_button_enabled(existing_device_row)) \
            .described_as("Edited row 'Remove' button to be enabled").is_false()

        edit_dialog.device_tree_picker.remove_selected_item(existing_device_type)
        assert_that(edit_dialog.device_tree_picker.get_all_selected_items()).is_empty()

        edit_dialog.device_tree_picker.select_device_types(new_device_type)
        edit_dialog.click_save()
        assert_that(edit_dialog.device_table.get_column_values(DeviceAssignmentTable.Headers.DEVICE_TYPES)) \
            .contains_only(new_device_type)

        edit_dialog.device_table.click_remove(new_device_type)
        assert_that(edit_dialog.device_table.rows).is_empty()

        edit_dialog.click_update()

        assert_that(users_page.notification.get_message()).is_equal_to(UsersPage.USER_UPDATED_MESSAGE)

        users_page.reload().search_by(new_user.email)

        assert_that(users_page.table.get_column_values(UsersTable.Headers.EMAIL)).contains_only(new_user.email)
        assert_that(users_page.table.get_name_by_email(new_user.email)).is_equal_to(new_user.name)
        assert_that(users_page.table.get_phone_by_email(new_user.email)).is_equal_to(new_user.phone_number)
        assert_that(users_page.table.get_user_group_by_email(new_user.email)).is_equal_to(new_user.user_group)
        assert_that(users_page.table.get_manager_by_email(new_user.email)).is_equal_to(new_user.manager)

    @allure.title("Add 8 devices. Verify pagination")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_user_dialog_pagination(self):
        test_region = Region.APAC
        test_device_group = DeviceType.ACUPULSE

        users_page = login_as(fota_admin_credentials)
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

    @allure.title("Create a new user with added device")
    @allure.severity(allure.severity_level.NORMAL)
    def test_associating_with_user_groups(self):
        users_page = login_as(super_admin_credentials)
        edit_dialog = open_first_test_user_from_table_to_edit(users_page)
        edit_dialog.select_user_group(UserGroup.SERVICE_ADMIN)

        all_managers = edit_dialog.manager_select.open().wait_to_be_not_empty().get_items()

        assert_that(all_managers).described_as("Managers list available for " + UserGroup.SERVICE_ADMIN + " group") \
            .contains(TEST_FOTA_ADMIN, TEST_SUPER_ADMIN) \
            .does_not_contain(TEST_SYSTEM_ENGINEER, TEST_SERVICE_ADMIN, TEST_TECH_SUPPORT)

    @allure.title("Edit user: device assignment")
    @allure.severity(allure.severity_level.NORMAL)
    def test_edit_user_assign_device(self):
        test_region = Region.AMERICAS
        test_country = "USA"
        test_state = "Colorado"
        test_device_group = DeviceType.ACUPULSE
        test_device_model = "Acupulse - 30W"
        test_device1 = "GA-0000070CN"

        expected_region = "{reg}/{country}/{state}".format(reg=test_region, country=test_country, state=test_state)
        expected_device_type = "{group}/{model}/{device}".format(group=test_device_group, model=test_device_model,
                                                                 device=test_device1)

        users_page = login_as(fota_admin_credentials)
        edit_dialog = open_first_test_user_from_table_to_edit(users_page)

        edit_dialog.location_tree_picker.select_usa_states(test_state)
        edit_dialog.device_tree_picker.select_devices(DeviceType.ACUPULSE, test_device_model, test_device1)
        edit_dialog.click_add_device()

        assert_that(edit_dialog.device_table.get_column_values(DeviceAssignmentTable.Headers.REGION)) \
            .contains(expected_region)
        assert_that(edit_dialog.device_table.get_column_values(DeviceAssignmentTable.Headers.DEVICE_TYPES)) \
            .contains(expected_device_type)

        edit_dialog.click_update()

        assert_that(users_page.notification.get_message()).is_equal_to(UsersPage.USER_UPDATED_MESSAGE)

    @allure.title("Reset password test")
    @allure.severity(allure.severity_level.NORMAL)
    def test_reset_users_password(self):
        users_page = login_as(super_admin_credentials)
        edit_dialog = open_first_test_user_from_table_to_edit(users_page)

        edit_dialog.click_reset_password()

        assert_that(users_page.notification.get_message()).is_equal_to(UsersPage.RESET_PASSWORD_MESSAGE)
        # TODO implement email client and add verification that 'Reset Password' email is received.


@allure.feature(Feature.USERS)
class TestDisableEnableUser:

    @allure.title("Disable user test")
    @allure.severity(allure.severity_level.NORMAL)
    def test_disable_user(self):
        user_email = user_for_disabling_credentials.username

        users_page = login_as(super_admin_credentials)
        edit_dialog = users_page.search_and_edit_user(user_email)
        edit_dialog.disable_user().click_update()
        users_page.table.wait_to_load()

        assert_that(users_page.notification.get_message()).is_equal_to(UsersPage.USER_UPDATED_MESSAGE)
        users_page.notification.close()

        assert_that(users_page.table.is_lock_icon_displayed(user_email))\
            .described_as("Lock icon to be displayed for the user " + user_email).is_true()

        users_page.logout()

        login_page = LoginPage().wait_to_load()
        login_page.unsuccessful_login(user_for_disabling_credentials.username, user_for_disabling_credentials.password)

        assert_that(login_page.notification.get_message()).is_equal_to(LoginPage.LOGIN_FAILURE_MESSAGE)
        assert_that(login_page.is_loaded()).described_as("Login Page to be opened").is_true()

    @allure.title("Enable user test")
    @allure.severity(allure.severity_level.NORMAL)
    def test_enable_user(self):
        user_email = user_for_disabling_credentials.username

        users_page = login_as(super_admin_credentials)
        edit_dialog = users_page.search_and_edit_user(user_email)
        edit_dialog.enable_user().click_update()
        users_page.table.wait_to_load()

        assert_that(users_page.notification.get_message()).is_equal_to(UsersPage.USER_UPDATED_MESSAGE)
        users_page.notification.close()

        assert_that(users_page.table.is_lock_icon_displayed(user_email))\
            .described_as("Lock icon to be displayed for the user " + user_email).is_false()

        users_page.logout()

        home_page = LoginPage().wait_to_load().login_as(user_for_disabling_credentials)

        home_page.background_image.should(be.visible)
