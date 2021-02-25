import random
import secrets
import string

import allure
from faker import Faker

from test.test_data_provider import TEST_USERS_EMAIL_DOMAIN

_faker = Faker()


@allure.step
def generate_random_item(input_list: []) -> str:
    return random.choice(input_list)


@allure.step
def generate_random_int_in_range(a, b) -> int:
    return random.randint(a, b)


@allure.step
def generate_random_string(length: int) -> str:
    return ''.join(random.choice(string.ascii_letters) for i in range(length))


@allure.step
def generate_random_numeric_string(length: int) -> str:
    return ''.join(random.choice(string.digits) for i in range(length))


@allure.step
def generate_random_alpha_numeric_string(length: int) -> str:
    source = string.ascii_letters + string.digits
    return ''.join((random.choice(source) for i in range(length)))


@allure.step
def generate_random_password(length: int) -> str:
    source = string.ascii_letters + string.digits + string.punctuation
    return ''.join((secrets.choice(source) for i in range(length)))


@allure.step
def generate_random_email() -> str:
    return _faker.email()


@allure.step
def generate_random_email_for_domain(domain: str) -> str:
    return generate_random_email().split("@", 1)[1] + domain


@allure.step
def generate_random_autotests_email() -> str:
    return generate_random_email_for_domain(TEST_USERS_EMAIL_DOMAIN)


@allure.step
def generate_random_user_name() -> str:
    return _faker.user_name()


@allure.step
def generate_random_first_name() -> str:
    return _faker.first_name()


@allure.step
def generate_random_last_name() -> str:
    return _faker.last_name()


@allure.step
def generate_random_name() -> str:
    return _faker.name()


@allure.step
def generate_random_phone_number() -> str:
    return _faker.phone_number()


@allure.step
def generate_random_address() -> str:
    return _faker.address()


@allure.step
def generate_random_city() -> str:
    return _faker.city()


@allure.step
def generate_random_company() -> str:
    return _faker.company()