from src.const import UserGroup
from src.domain.credentials import Credentials
from src.domain.user import User
from src.util.random_util import *

TEST_USERS_EMAIL_DOMAIN = "@auto.test"
TEST_USER_NAME = "Victor savchyn"

super_admin_credentials = Credentials("victor.savchyn@gmail.com", "LumenisX225")
service_manager_credentials = Credentials("victor.savchyn+serviceManager@gmail.com", "LumenisX225")


def generate_random_user():
    return User(first_name=generate_random_first_name(),
                last_name=generate_random_last_name(),
                email=generate_random_autotests_email,
                phone_number=generate_random_phone_number,
                user_group=generate_random_item([UserGroup.SERVICE_MANAGER, UserGroup.TECH_SUPPORT,
                                                 UserGroup.SERVICE_TECHNICIAN]),
                manager=TEST_USER_NAME)
