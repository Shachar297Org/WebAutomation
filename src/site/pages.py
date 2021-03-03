import abc
import time

import allure
from selene.api import s
from selene.core import query
from selene.support.conditions import be, have
from selene.support.shared import browser

from src.domain.user import User
from src.site.components.page_header import PageHeader
from src.site.components.simple_components import SearchInput, SelectBox
from src.site.components.tables import UsersTable
from src.site.dialogs import CreateUserDialog, EditUserDialog
from src.util.elements_util import JS_CLICK


class _BasePage:
    def __init__(self):
        self.logo_img = s("section img")
        self.version = s("//section[contains(@class, 'Logo__Version')]")

        self.left_panel = _LeftPanel(".ant-menu.ant-menu-inline")
        self.header = PageHeader("ant-layout-header")

        self.notification_msg = s(".ant-notification-notice-message")
        self.notification_description = s(".ant-notification-notice-description")

        self.style = s("body style")

    @abc.abstractmethod
    def open(self):
        """"Method should open the page by URL"""

    @abc.abstractmethod
    def wait_to_load(self):
        """"Method should check if the page is loaded by some unique conditions
        (wait to some element that exists only for the particular page)"""

    @allure.step
    def get_version(self) -> str:
        return self.version.get(query.text)

    @allure.step
    def get_logo_img_url(self) -> str:
        return self.logo_img.get(query.attribute("src"))

    @allure.step
    def get_notification_message(self):
        self._wait_for_notification()
        return self.notification_msg.get(query.text)

    @allure.step
    def get_notification_description(self):
        self._wait_for_notification()
        return self.notification_description.get(query.text)

    @allure.step
    def _wait_for_notification(self):
        self.notification_msg.wait.until(be.visible)


class HomePage(_BasePage):
    def __init__(self):
        super().__init__()
        self.background_image = s("//div[contains(@class, 'HomePage__BackgroundImage')]")

    @allure.step
    def open(self):
        browser.open('/home')
        self.wait_to_load()
        return self

    def wait_to_load(self):
        self.background_image.wait_until(be.visible)
        return self


class UsersPage(_BasePage):
    SEARCH_LABEL = "Search"
    SELECT_USERS_GROUP_LABEL = "Select User Group..."

    USER_CREATED_MESSAGE = "Create User successful"
    USER_UPDATED_MESSAGE = "Update User successful"

    def __init__(self):
        super().__init__()
        self.add_button = s("//button[span[text()='+']]")
        self.search_input = SearchInput("input[placeholder='Search']")
        self.user_group_select = SelectBox("#entityToolbarFilters_userGroupFilter")
        self.reset_button = s("//button[span[text()='Reset']]")
        self.reload_button = s("i.anticon-reload")
        self.table = UsersTable(".ant-table-wrapper")

    @allure.step
    def open(self):
        browser.open('/users')
        self.wait_to_load()
        return self

    def wait_to_load(self):
        self.add_button.wait_until(be.visible)
        return self

    @allure.step
    def sort_asc_by(self, column: str):
        self.table.sort_asc(column)
        return self

    @allure.step
    def sort_desc_by(self, column: str):
        self.table.sort_desc(column)
        return self

    @allure.step
    def search_by(self, text: str):
        self.search_input.search(text)
        return self

    @allure.step
    def filter_by_group(self, user_group: str):
        self.user_group_select.select_item(user_group)
        time.sleep(2)  # TODO workaround, replace with the waiter
        return self

    @allure.step
    def add_user(self, user: User):
        self.click_add_user().set_user_fields(user).click_create()
        return self

    @allure.step
    def open_edit_user_dialog(self, email):
        self.table.click_edit(email)
        return EditUserDialog().wait_to_load()

    @allure.step
    def click_add_user(self) -> CreateUserDialog:
        self.add_button.click()
        return CreateUserDialog().wait_to_load()

    @allure.step
    def click_reset(self):
        self.reset_button.click()
        self.reset_button.wait.until(have.attribute("ant-click-animating-without-extra-node").value("false"))
        return self

    @allure.step
    def reload(self):
        self.reload_button.execute_script(JS_CLICK)
        return UsersPage()


class DevicesPage(_BasePage):
    def __init__(self):
        super().__init__()
        self.add_button = s("//button[span[text()='+']]")
        self.reset_button = s("//button[span[text()='Reset']]")
        self.reload_button = s("i.anticon - reload")

    @allure.step
    def open(self):
        browser.open('/devices')
        self.wait_to_load()
        return self

    def wait_to_load(self):
        self.add_button.wait_until(be.visible)
        return self

    @allure.step
    def _click_add_device(self):
        self.add_button.click()
        return self


class AlarmsPage(_BasePage):
    def __init__(self):
        super().__init__()
        self.reset_button = s("//button[span[text()='Reset']]")
        self.reload_button = s("i.anticon - reload")

    @allure.step
    def open(self):
        browser.open('/alarms')
        self.wait_to_load()
        return self

    def wait_to_load(self):
        self.reset_button.wait_until(be.visible)
        return self

    @allure.step
    def _click_reset(self):
        self.reset_button.click()


class QlikPage(_BasePage):

    @allure.step
    def open(self):
        browser.open('/qlik')
        return self

    def wait_to_load(self):
        print("TBD")


class _LeftPanel(object):
    def __init__(self, locator: str):
        self.panel = s(locator)
        self.panel.wait_until(be.visible)

        self.home_section = self.panel.s("a[href='/']")
        self.users_section = self.panel.s("a[href='/users']")
        self.devices_section = self.panel.s("a[href='/devices']")
        self.alarms_section = self.panel.s("a[href='/alarms']")
        self.qlik_section = self.panel.s("a[href='/qlik']")

    @allure.step
    def open_home(self) -> HomePage:
        self.home_section.click()
        return HomePage().wait_to_load()

    @allure.step
    def open_users(self) -> UsersPage:
        self.users_section.click()
        return UsersPage().wait_to_load()

    @allure.step
    def open_devices(self) -> DevicesPage:
        self.devices_section.click()
        return DevicesPage().wait_to_load()

    @allure.step
    def open_alarms(self) -> AlarmsPage:
        self.alarms_section.click()
        return AlarmsPage().wait_to_load()

    @allure.step
    def open_qlik(self) -> QlikPage:
        self.qlik_section.click()
        return QlikPage()
