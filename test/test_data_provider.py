from src.const import UserGroup
from src.domain.credentials import Credentials
from src.domain.user import User
from src.util.random_util import random_first_name, random_last_name, \
    random_phone_number, random_list_item, random_gmail_alias_from


TEST_SUPER_ADMIN = "Victor savchyn"
TEST_FOTA_ADMIN = "Victor AQA FOTA Admin"
TEST_SYSTEM_ENGINEER = "Victor AQA System Engineer"
TEST_SERVICE_ADMIN = "Victor AQA Service Admin"
TEST_TECH_SUPPORT = "Victor AQA Tech Support"

TEST_USER_FOR_DISABLING = "Victor AQA User For Disabling"

TEST_USERS_PREFIX = "lumenisauto+test"
TEST_GMAIL_ACCOUNT = "lumenisauto@gmail.com"

super_admin_credentials = Credentials("victor.savchyn@gmail.com", "LumenisX225")
fota_admin_credentials = Credentials("lumenisauto+FotaAdmin@gmail.com", "LumenisX225@")
system_engineer_credentials = Credentials("lumenisauto+SystemEngineer@gmail.com", "LumenisX225@")
service_admin_credentials = Credentials("lumenisauto+ServiceAdmin@gmail.com", "LumenisX225@")
tech_support_credentials = Credentials("lumenisauto+TechSupport@gmail.com", "LumenisX225@")

user_for_disabling_credentials = Credentials("lumenisauto+Disabled@gmail.com", "LumenisX225@")


def generate_random_user():
    return User(first_name=random_first_name(),
                last_name=random_last_name(),
                email=random_gmail_alias_from(TEST_GMAIL_ACCOUNT),
                phone_number=random_phone_number(),
                user_group=random_list_item([UserGroup.SERVICE_MANAGER, UserGroup.TECH_SUPPORT,
                                             UserGroup.SERVICE_TECHNICIAN]),
                manager=TEST_FOTA_ADMIN)
