import allure
from selene.core import query
from selene.support.conditions import be
from selene.support.shared.jquery_style import s


class PageHeader:
    def __init__(self, locator):
        self.header = s(locator)
        self.fold_icon = self.header.s("i.anticon-menu-fold")
        self.unfold_icon = self.header.s("i.anticon-menu-unfold")

        self.username = self.header.s(".ant-typography")
        self.user_avatar = self.header.s(".ant-avatar.ant-dropdown-trigger")

        self.user_preferences_button = self.header.s("//button[./span[text()='User Preferences']]")
        self.logout_button = self.header.s("//button[./span[text()='Logout']]")

    @allure.step
    def fold_panel(self):
        if self.fold_icon.matching(be.visible):
            self.fold_icon.click()
        return self

    @allure.step
    def unfold_panel(self):
        if self.unfold_icon.matching(be.visible):
            self.unfold_icon.click()
        return self

    @allure.step
    def get_username(self) -> str:
        return self.username.get(query.text)

    @allure.step
    def open_user_preferences(self):
        self.user_avatar.hover()
        self.user_preferences_button.wait_until(be.clickable)
        self.user_preferences_button.click()
        return UserPreferences()

    @allure.step
    def logout(self):
        self.user_avatar.should(be.clickable).click()
        self.logout_button.should(be.clickable).should(be.visible)
        self.logout_button.click()


class UserPreferences:
    def __init__(self):
        self.email_checkbox = s("input[value=emailAlarm]")
        self.text_message_checkbox = s("input[value=smsAlarm]")

        self.email_checkbox.wait_until(be.clickable)
