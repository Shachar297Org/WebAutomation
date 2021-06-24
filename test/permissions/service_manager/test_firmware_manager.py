import allure
from selene.support.conditions import be

from src.const import Feature
from src.site.login_page import LoginPage

from test.test_data_provider import service_manager_credentials


@allure.feature(Feature.PERMISSIONS)
@allure.title("3.1.8.3 Service manager: firmware manager permissions")
@allure.severity(allure.severity_level.NORMAL)
def test_firmware_manager_permissions():
    home_page = LoginPage().open().login_as(service_manager_credentials)

    home_page.left_panel.firmware_manager_section.should(be.not_.present)
