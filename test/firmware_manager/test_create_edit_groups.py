import allure
import pytest
from assertpy import assert_that
from selene.support.conditions import be, have

from src.const import Feature, Region, APAC_Country, DeviceGroup, AcupulseDeviceModels, Acupulse30Wdevices
from src.domain.credentials import Credentials
from src.site.components.tables import GroupsTable
from src.site.components.tree_selector import SEPARATOR
from src.site.dialogs import get_element_label, assert_text_input_default_state, \
    assert_tree_selector_default_state, CreateGroupDialog
from src.site.login_page import LoginPage
from src.site.pages import GroupsPage
from src.util.driver_util import clear_session_storage, clear_local_storage
from src.util.random_util import random_string
from test.test_data_provider import fota_admin_credentials


@pytest.fixture(autouse=True)
def cleanup_browser_session():
    yield
    clear_session_storage()
    clear_local_storage()


def login_as(credentials: Credentials):
    LoginPage().open().login_as(credentials)
    return GroupsPage().open()


@allure.feature(Feature.FW_MANAGER)
class TestCreateEditGroups:

    @allure.title("Verify 'Create Group' dialog web elements")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_group_dialog_elements(self):
        groups_page = login_as(fota_admin_credentials)
        dialog = groups_page.click_add_group()

        dialog.title.should(have.exact_text(CreateGroupDialog.TITLE))
        assert_text_input_default_state(dialog.group_name_input, CreateGroupDialog.GROUP_NAME_LABEL)

        assert_that(get_element_label(dialog.device_type_tree_selector.tree_selector)) \
            .described_as("Device type label").is_equal_to(CreateGroupDialog.DEVICE_TYPE_FAMILY_LABEL)
        dialog.device_type_tree_selector.tree_selector.should(be.visible)
        assert_that(dialog.device_type_tree_selector.selected_items()) \
            .described_as("'Device type' tree selector to be empty").is_empty()

        assert_tree_selector_default_state(dialog.locations_tree_selector, CreateGroupDialog.LOCATIONS_PLACEHOLDER)
        assert_that(get_element_label(dialog.locations_tree_selector.tree_selector)).described_as("Locations label") \
            .is_equal_to(CreateGroupDialog.LOCATIONS_LABEL)

        dialog.create_button.should(be.visible).should(be.clickable)
        dialog.cancel_button.should(be.visible).should(be.clickable)

    @allure.title("Create a new group")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_group(self):
        test_group_name = "autotests_" + random_string(8)
        test_region = Region.APAC
        test_country1 = APAC_Country.CHINA
        test_country2 = APAC_Country.INDIA
        test_device_group = DeviceGroup.ACUPULSE
        test_device_model = AcupulseDeviceModels.ACUPULSE_30W
        test_device = Acupulse30Wdevices.GA_0000070CN
        headers = GroupsTable.Headers

        groups_page = login_as(fota_admin_credentials)
        dialog = groups_page.click_add_group()

        dialog.set_group_name(test_group_name) \
            .select_device(test_device) \
            .select_countries(test_region, test_country1, test_country2) \
            .click_create()

        assert_that(groups_page.notification.get_message()).is_equal_to(GroupsPage.GROUP_CREATED_MESSAGE)

        groups_page.reload().search_by(test_group_name)

        assert_that(groups_page.table.get_column_values(headers.NAME)).contains(test_group_name)
        created_row = groups_page.table.get_row_by_name(test_group_name)

        assert_that(created_row.get_cell_text(headers.DEVICE_TYPE)) \
            .is_equal_to(test_device_group + SEPARATOR + test_device_model + SEPARATOR + test_device)
        assert_that(created_row.get_cell_text(headers.REGION)).is_equal_to(test_region)
        assert_that(created_row.get_cell_text(headers.COUNTRY)).is_equal_to(test_country1 + ", " + test_country2)

        assert_that(groups_page.table.is_row_contains_edit_button(created_row)) \
            .described_as("Edit button").is_true()
        assert_that(groups_page.table.is_row_contains_assign_device_button(created_row)) \
            .described_as("Assign device button").is_true()
        assert_that(groups_page.table.is_row_contains_update_version_button(created_row)) \
            .described_as("Update version button").is_true()
        assert_that(groups_page.table.is_row_contains_status_button(created_row)) \
            .described_as("Status button").is_true()
