import pytest
import sys
import argparse
from create_devices_activate import * 
import time

parser=argparse.ArgumentParser()

parser.add_argument('--swPath', help='Software path', default="D:/SWFOTA/swDesiredVersionCheck3.0.0_Force_Signed.exe")
parser.add_argument('--swVersion', help='Software version', default="3.0.0")
parser.add_argument('--deviceFamily', help='Devices root name', default="TEST-SWFOTA-C")
parser.add_argument('--deviceType', help='Devices type', default="GA-0000180")
parser.add_argument('--deviceModel', help='Devices model', default="Acupulse - 40W ST")
parser.add_argument('--swFileType', help='Software file type', default="TESTER_APP")
parser.add_argument('--swSupportedVersion', help='Software supported version', default="*")
parser.add_argument('--swInstallType', help='Software install type', default="Force")
parser.add_argument('--numberOfDevices', help='Number of devices', default="1")
parser.add_argument('--times', help='Times to run one test', default="1")

args=parser.parse_args()

if __name__ == "__main__":

    #accessToken = SendRequestLogin()
#
    #for index in range(int(args.numberOfDevices)):
    #    device = {
    #        'deviceSerialNumber': "{0}-{1}".format(args.devicesFamily, index + 1),
    #        'deviceType': args.deviceType
    #    }
    #    InsertDevice(accessToken, device)
    #    ActivateDevice(accessToken, device)
    

    args_list = ["-n", "1", "test_sw_fota.py::TestSWFOTA::test_sw_fota_multiple_times", "--swPath", args.swPath, "--swVersion", args.swVersion, "--deviceFamily", args.deviceFamily, "--deviceType", args.deviceType, "--deviceModel", args.deviceModel,
                 "--swFileType", args.swFileType, "--swSupportedVersion", args.swSupportedVersion, "--swInstallType", args.swInstallType, "--numberOfDevices", args.numberOfDevices, "--times", args.times]
#
    retcode = pytest.main(args_list)
    sys.exit(retcode)