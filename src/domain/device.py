class Customer(object):
    def __init__(self,
                 clinic_name: str = None,
                 first_name: str = None,
                 last_name: str = None,
                 email: str = None,
                 phone_number: str = None,
                 clinic_id: str = None,
                 street: str = None,
                 street_number: str = None,
                 city: str = None,
                 postal_zip: str = None,
                 region_country: str = None,
                 state: str = None,
                 comments: str = None):
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
    def __init__(self, serial_number: str = None,
                 group: str = None,
                 model: str = None,
                 device: str = None):
        self.serial_number = serial_number
        self.group = group
        self.model = model
        self.device = device
