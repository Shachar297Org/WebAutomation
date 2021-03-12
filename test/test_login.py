import allure
import pytest
from assertpy import assert_that
from selene.core import query
from selene.support.conditions import have

from src.const import Feature
from src.site.login_page import LoginPage
from selene.api import be

from src.util.driver_util import *
from test.test_data_provider import super_admin_credentials

USERNAME = super_admin_credentials.username
PASSWORD = super_admin_credentials.password


@pytest.fixture(autouse=True)
def cleanup_browser_session():
    yield
    clear_session_storage()
    clear_local_storage()


# TODO Extends the test suite with all documented login tests
@pytest.mark.usefixtures("setup_driver")
@allure.feature(Feature.LOGIN)
class TestLogin:
    wrong_credentials_provider = [
        (USERNAME, PASSWORD.upper(), LoginPage.INVALID_PASSWORD_MESSAGE),
        (USERNAME, PASSWORD.lower(), LoginPage.INVALID_PASSWORD_MESSAGE),
        (USERNAME, " ", LoginPage.INVALID_PASSWORD_MESSAGE),
        (USERNAME[:-1], PASSWORD, LoginPage.USER_DOESNT_EXIST_MESSAGE),
    ]

    @allure.title("Verify Login page web elements")
    @allure.severity(allure.severity_level.NORMAL)
    def test_page_elements(self):
        login_page = LoginPage().open()

        login_page.username_input.should(be.visible).should(be.clickable)
        assert_that(login_page.username_input.get(query.text)).is_empty()

        login_page.password_input.should(be.visible).should(be.clickable)
        assert_that(login_page.password_input.get(query.text)).is_empty()

        login_page.login_button.should(be.visible).should(be.clickable)

        login_page.forgot_password_link.should(be.visible).should(be.clickable)

        login_page.logo.should(be.visible)
        login_page.welcome_title.should(be.visible).should(have.exact_text(LoginPage.WELCOME_TEXT))
        login_page.version.should(be.visible)
        assert_that(login_page.version.get(query.text)).is_not_empty()

        login_page.notification.should_not_be_visible()

    @allure.title("Verify that a user can login into the portal")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_successful_login(self, cleanup_browser_session):
        home_page = LoginPage().open().login(USERNAME, PASSWORD)

        home_page.left_panel.panel.should(be.present).should(be.clickable)

        print(get_local_storage())  # added for the demo

    @allure.title("Verify that a user can't login into the portal with invalid credentials {username} {password}")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("username, password, error", wrong_credentials_provider)
    def test_login_with_wrong_credentials(self, username, password, error):
        login_page = LoginPage().open()
        login_page.unsuccessful_login(username, password)

        assert_that(login_page.notification.get_description()).is_equal_to(error)
        assert_that(login_page.is_loaded()).described_as("Login page to be opened").is_true()
