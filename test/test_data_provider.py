from src.const import UserGroup
from src.domain.credentials import Credentials
from src.domain.user import User
from src.util.random_util import random_first_name, random_last_name, \
    random_phone_number, random_list_item, random_gmail_alias_from


TEST_USER_NAME = "Victor savchyn"

TEST_GMAIL_ACCOUNT = "lumenisauto@gmail.com"
super_admin_credentials = Credentials("victor.savchyn@gmail.com", "LumenisX225")
fota_admin_credentials = Credentials("lumenisauto+FotaAdmin@gmail.com", "LumenisX225@")
service_manager_credentials = Credentials("victor.savchyn+serviceManager@gmail.com", "LumenisX225")


def generate_random_user():
    return User(first_name=random_first_name(),
                last_name=random_last_name(),
                email=random_gmail_alias_from(TEST_GMAIL_ACCOUNT),
                phone_number=random_phone_number(),
                user_group=random_list_item([UserGroup.SERVICE_MANAGER, UserGroup.TECH_SUPPORT,
                                             UserGroup.SERVICE_TECHNICIAN]),
                manager=TEST_USER_NAME)
