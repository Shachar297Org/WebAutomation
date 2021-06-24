import allure
from assertpy import assert_that

from src.domain.device import Device, Customer
from src.site.components.cascader_picker import SEPARATOR
from src.site.components.tables import DevicesTable


class BaseDevicesTest:

    @allure.step
    def assert_device_in_table(self, table: DevicesTable, expected: Device):
        assert_that(table.get_column_values(table.Headers.SERIAL_NUMBER)).contains_only(expected.serial_number)
        assert_that(table.get_column_values(table.Headers.DEVICE_TYPE)).contains_only(
            expected.model + SEPARATOR + expected.device)
        assert_that(table.get_column_values(table.Headers.STATUS)).contains_only(table.INACTIVE_STATUS)
        assert_that(table.device_has_properties_button(expected.serial_number)).described_as("Properties link").is_true()

    @allure.step
    def assert_customer_in_table(self, table: DevicesTable, expected: Customer):
        assert_that(table.get_column_values(table.Headers.CLINIC_ID)).contains_only(expected.clinic_id)
        assert_that(table.get_column_values(table.Headers.CLINIC_NAME)).contains_only(expected.clinic_name)
        assert_that(table.get_column_values(table.Headers.COUNTRY)).contains_only(expected.region_country)
