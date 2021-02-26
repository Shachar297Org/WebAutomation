import random
import secrets
import string

import allure
from faker import Faker

_faker = Faker()


@allure.step
def random_list_item(input_list: []) -> str:
    return random.choice(input_list)


@allure.step
def random_int_in_range(a, b) -> int:
    return random.randint(a, b)


@allure.step
def random_string(length: int) -> str:
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))


@allure.step
def random_numeric_string(length: int) -> str:
    return ''.join(random.choice(string.digits) for _ in range(length))


@allure.step
def random_alpha_numeric_string(length: int) -> str:
    source = string.ascii_letters + string.digits
    return ''.join((random.choice(source) for _ in range(length)))


@allure.step
def random_password(length: int) -> str:
    source = string.ascii_letters + string.digits + string.punctuation
    return ''.join((secrets.choice(source) for _ in range(length)))


@allure.step
def random_email() -> str:
    return _faker.email()


@allure.step
def random_email_for_domain(domain: str) -> str:
    return random_email().split("@", 1)[0] + domain


@allure.step
def random_gmail_alias_from(gmail_email: str) -> str:
    return gmail_email.split("@", 1)[0] + "+test" + random_numeric_string(8) + "@gmail.com"


@allure.step
def random_user_name() -> str:
    return _faker.user_name()


@allure.step
def random_first_name() -> str:
    return _faker.first_name()


@allure.step
def random_last_name() -> str:
    return _faker.last_name()


@allure.step
def random_name() -> str:
    return _faker.name()


@allure.step
def random_phone_number() -> str:
    return _faker.phone_number()


@allure.step
def random_address() -> str:
    return _faker.address()


@allure.step
def random_city() -> str:
    return _faker.city()


@allure.step
def random_company() -> str:
    return _faker.company()


if __name__ == '__main__':
    print("")
