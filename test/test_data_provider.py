import allure

from src.const import UserGroup, Acupulse30Wdevices, EMEA_Country, AcupulseDeviceModels, DeviceType
from src.domain.credentials import Credentials
from src.domain.device import Device, Customer
from src.domain.user import User
from src.util.random_util import random_first_name, random_last_name, \
    random_phone_number, random_list_item, random_gmail_alias_from, random_numeric_string, random_email, random_city, \
    random_string, random_alpha_numeric_string, random_company, random_user_name, random_zip_code, \
    random_street_address, random_state

TEST_SUPER_ADMIN = "Victor savchyn"
TEST_FOTA_ADMIN = "Victor AQA FOTA Admin"
TEST_SYSTEM_ENGINEER = "Victor AQA System Engineer"
TEST_SERVICE_ADMIN = "Victor AQA Service Admin"
TEST_TECH_SUPPORT = "Victor AQA Tech Support"

TEST_USER_FOR_DISABLING = "Victor AQA User For Disabling"

TEST_DEVICE_PREFIX = "AUTOTESTS-"
TEST_USERS_PREFIX = "lumenisauto+test"
TEST_GMAIL_ACCOUNT = "lumenisauto@gmail.com"

super_admin_credentials = Credentials("victor.savchyn@gmail.com", "LumenisX225")
fota_admin_credentials = Credentials("lumenisauto+FotaAdmin@gmail.com", "LumenisX225@")
system_engineer_credentials = Credentials("lumenisauto+SystemEngineer@gmail.com", "LumenisX225@")
service_admin_credentials = Credentials("lumenisauto+ServiceAdmin@gmail.com", "LumenisX225@")
tech_support_credentials = Credentials("lumenisauto+TechSupport@gmail.com", "LumenisX225@")

user_for_disabling_credentials = Credentials("lumenisauto+Disabled@gmail.com", "LumenisX225@")

test_device_group = DeviceType.ACUPULSE
test_device_model = AcupulseDeviceModels.ACUPULSE_30W


@allure.step
def random_user():
    return User(first_name=random_first_name(),
                last_name=random_last_name(),
                email=random_gmail_alias_from(TEST_GMAIL_ACCOUNT),
                phone_number=random_phone_number(),
                user_group=random_list_item([UserGroup.SERVICE_MANAGER, UserGroup.TECH_SUPPORT,
                                             UserGroup.SERVICE_TECHNICIAN]),
                manager=TEST_FOTA_ADMIN)


@allure.step
def random_device():
    return Device(serial_number=TEST_DEVICE_PREFIX + random_numeric_string(8),
                  device_type=random_list_item([Acupulse30Wdevices.GA_0000070CN, Acupulse30Wdevices.GA_0000070DE,
                                                Acupulse30Wdevices.GA_0000070GR, Acupulse30Wdevices.RG_0000070]))


@allure.step
def random_customer():
    return Customer(clinic_name=random_company(),
                    first_name=random_first_name(),
                    last_name=random_last_name(),
                    email=random_email(),
                    phone_number=random_phone_number(),
                    clinic_id=random_numeric_string(10),
                    street=random_street_address(),
                    street_number=random_numeric_string(1),
                    city=random_city(),
                    postal_zip=random_zip_code(),
                    region_country=random_list_item(EMEA_Country.POLAND, EMEA_Country.GERMANY, EMEA_Country.AUSTRIA,
                                                    EMEA_Country.UKRAINE, EMEA_Country.UNITED_KINGDOM),
                    comments=random_alpha_numeric_string(20))


@allure.step
def random_usa_customer():
    return Customer(clinic_name=random_company(),
                    first_name=random_first_name(),
                    last_name=random_last_name(),
                    email=random_email(),
                    phone_number=random_phone_number(),
                    clinic_id=random_numeric_string(10),
                    street=random_street_address(),
                    street_number=random_numeric_string(1),
                    city=random_city(),
                    postal_zip=random_zip_code(),
                    region_country="USA",
                    state=random_state(),
                    comments=random_string(10) + " " + random_string(10))
