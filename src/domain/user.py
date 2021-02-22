class User(object):
    def __init__(self,
                 first_name: str,
                 last_name: str,
                 email: str,
                 phone_number: str,
                 user_group: str,
                 manager: str):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone_number = phone_number
        self.user_group = user_group
        self.manager = manager
