import allure
from selene.api import *
from selene.support.shared import browser

from src.domain.credentials import Credentials
from src.site.components.simple_components import TopRightNotification
from src.site.pages import HomePage


class LoginPage(object):
    WELCOME_TEXT = "Welcome to LumenisX"

    INVALID_PASSWORD_MESSAGE = "Password is not valid"
    USER_DOESNT_EXIST_MESSAGE = 'User does not exist'
    LOGIN_FAILURE_MESSAGE = 'Login Failure'

    def __init__(self):
        self.username_input = s("#loginForm_username")
        self.password_input = s("#loginForm_password")
        self.login_button = s(by.xpath("//button[@type='submit']"))
        self.forgot_password_link = s(by.xpath("//button[@type='button']"))

        self.notification = TopRightNotification()

        self.welcome_title = s("h2.ant-typography")
        self.logo = s("//img[@alt='LumenisX']")
        self.version = s("//section[contains(@class, 'AppVersion')]")

    @allure.step
    def open(self):
        browser.open('/')
        browser.driver.set_page_load_timeout(10)

        self.username_input.wait.until(be.visible)
        return self

    @allure.step
    def wait_to_load(self):
        self.password_input.wait_until(be.visible)
        self.login_button.matching(be.clickable)
        return self

    @allure.step
    def is_loaded(self):
        return self.username_input.matching(be.visible) & self.password_input.matching(be.visible) \
               & self.login_button.matching(be.clickable)

    @allure.step
    def login(self, username: str, password: str) -> HomePage:
        self._enter_username(username)
        self._enter_password(password)
        self._click_login()
        return HomePage()

    def login_as(self, credentials: Credentials) -> HomePage:
        return self.login(credentials.username, credentials.password)

    @allure.step
    def unsuccessful_login(self, username: str, password: str):
        self._enter_username(username)
        self._enter_password(password)
        self._click_login()
        return self

    @allure.step
    def _enter_username(self, username: str):
        self.username_input.set_value(username)

    @allure.step
    def _enter_password(self, password: str):
        self.password_input.set_value(password)

    @allure.step
    def _click_login(self):
        self.login_button.click()
