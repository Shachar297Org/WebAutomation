class Customer(object):
    def __init__(self,
                 clinic_name="",
                 first_name="",
                 last_name="",
                 email="",
                 phone_number="",
                 clinic_id="",
                 street="",
                 street_number="",
                 city="",
                 postal_zip="",
                 region_country="",
                 state="",
                 comments=''):
        self.clinic_name = clinic_name
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone_number = phone_number
        self.clinic_id = clinic_id
        self.street = street
        self.street_number = street_number
        self.city = city
        self.postal_zip = postal_zip
        self.region_country = region_country
        self.state = state
        self.comments = comments


class Device(object):
    def __init__(self, serial_number: str, device_type: str):
        self.serial_number = serial_number
        self.device_type = device_type
