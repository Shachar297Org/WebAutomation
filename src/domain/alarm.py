class Alarm(object):
    def __init__(self,
                 date: str,
                 alarm_id: str,
                 description: str,
                 device_id: str,
                 device_type: str):
        self.date = date
        self.alarm_id = alarm_id
        self.description = description
        self.device_id = device_id
        self.device_type = device_type
