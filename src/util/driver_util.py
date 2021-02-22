from selene.support.shared import browser


def get_local_storage():
    return browser.driver.execute_script("return window.localStorage;")


def get_session_storage():
    return browser.driver.execute_script("return window.sessionStorage;")


def clear_local_storage():
    browser.driver.execute_script("localStorage.clear()")


def clear_session_storage():
    browser.driver.execute_script("sessionStorage.clear()")
