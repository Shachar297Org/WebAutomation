import requests
import json

config = {
    'API_LOGIN_HOST': "https://api.int.lumenisx.lumenis.com/ums/v1/users/loginCredentials",
    'API_USER': "vkrytskyy@gmail.com",
    'API_PASS': "tq5AhV72KA7YEgs",
    'API_INSERT_DEVICE': "https://api.int.lumenisx.lumenis.com/facade/v1/device",
    'API_GENERATE_CERTIFICATES': "https://api.int.lumenisx.lumenis.com/device/v1/lumDevice/generateCertificate/types/{0}/serialNumbers/{1}",
    'API_ACK_CERTIFICATE': "https://api.int.lumenisx.lumenis.com/device/v1/lumDevice/types/{0}/serialNumbers/{1}/acknowledgeCertificate",
    'CLIENT_PATH': "",
    'SERVER_PATH': "",
    'DEVICES_FOLDER': "D:/DeviceFolder/"
}


def SendRequestLogin():
    """
    Sends to api host login request and return access token
    """
    loginHost = config['API_LOGIN_HOST']
    loginData = {
        "email": config['API_USER'],
        "password": config['API_PASS']
    }
    response = requests.post(
        url=loginHost, headers={'Content-Type': 'application/json'}, data=json.dumps(loginData))
    if not response.ok:
        print('Request failed. status code: {}'.format(response.status_code))
        return None
    jsonObj = response.json()
    return jsonObj['accessToken']


def InsertDevice(accessToken: str, deviceRecord: dict):
    """
    Insert new device to portal using access token
    """
    host = config['API_INSERT_DEVICE']
    response = requests.post(url=host, headers={'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(
        accessToken)}, data=json.dumps({'createLumDeviceRequest': deviceRecord}))
    if response.ok:
        print('Device device {} was inserted successfully.'.format(deviceRecord))
    else:
        print('Error: cannot insert device {}. status code: {}. {}'.format(
            deviceRecord, response.status_code, response.text))



def ActivateDevice(accessToken: str, deviceRecord: dict):
    """
    Insert new device to portal using access token
    """
    host = config['API_GENERATE_CERTIFICATES'].format(deviceRecord["deviceType"], deviceRecord["deviceSerialNumber"])
    #print(host)

    response = requests.get(url=host, headers={'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(
        accessToken)})

    if response.ok:
        print(response)
        host = config['API_ACK_CERTIFICATE'].format(deviceRecord["deviceType"], deviceRecord["deviceSerialNumber"])
        print(host)

        response = requests.post(url=host, headers={'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(
                accessToken)})

        if response.ok:
            print('Device {} was activated successfully.'.format(deviceRecord))
        else:
            print('Error: cannot activate device {}. status code: {}. {}'.format(
                deviceRecord, response.status_code, response.text))
    else:
        print('Error: cannot generate certificate for device {}. status code: {}. {}'.format(
            deviceRecord, response.status_code, response.text))

