import pytest
import os

if os.getenv('_PYTEST_RAISE', "0") != "0":

    @pytest.hookimpl(tryfirst=True)
    def pytest_exception_interact(call):
        raise call.excinfo.value

    @pytest.hookimpl(tryfirst=True)
    def pytest_internalerror(excinfo):
        raise excinfo.value

def pytest_addoption(parser):

    parser.addoption('--swPath', help='Software path')
    parser.addoption('--swVersion', help='Software version')
    parser.addoption('--deviceFamily', help='Devices root name')
    parser.addoption('--deviceType', help='Devices type')
    parser.addoption('--deviceModel', help='Devices model')
    parser.addoption('--deviceGroup', help='Devices group')
    parser.addoption('--swFileType', help='Software file type')
    parser.addoption('--swSupportedVersion', help='Software supported version')
    parser.addoption('--swInstallType', help='Software install type')
    parser.addoption('--numberOfDevices', help='Number of devices')
    parser.addoption('--times', help='Times to run one test')


@pytest.hookimpl
def pytest_generate_tests(metafunc):
    if "swPath" in metafunc.fixturenames:
        
        swPath = metafunc.config.getoption("--swPath")
        swVersion = metafunc.config.getoption("--swVersion")
        devicesFamily = metafunc.config.getoption("--deviceFamily")
        deviceType = metafunc.config.getoption("--deviceType")
        deviceModel = metafunc.config.getoption("--deviceModel")
        deviceGroup = metafunc.config.getoption("--deviceGroup")
        swFileType = metafunc.config.getoption("--swFileType")
        swSupportedVersion = metafunc.config.getoption("--swSupportedVersion")
        swInstallType = metafunc.config.getoption("--swInstallType")
        
        numberOfDevices = range(int(metafunc.config.getoption("--numberOfDevices")))
        params = []
        deviceSNs = []
        for index in numberOfDevices:
            deviceSN = "{0}-{1}".format(devicesFamily, index + 1)
            deviceSNs.append(deviceSN)
            params.append((swPath,swVersion,deviceSN,deviceType,deviceModel,deviceGroup,swFileType,swSupportedVersion,swInstallType))

        metafunc.parametrize("swPath", [str(swPath)])
        metafunc.parametrize("swVersion", [str(swVersion)])
        metafunc.parametrize("deviceSN", deviceSNs)
        metafunc.parametrize("deviceType", [str(deviceType)])
        metafunc.parametrize("deviceModel", [str(deviceModel)])
        metafunc.parametrize("deviceGroup", [str(deviceGroup)])
        metafunc.parametrize("swFileType", [str(swFileType)])
        metafunc.parametrize("swSupportedVersion", [str(swSupportedVersion)])
        metafunc.parametrize("swInstallType", [str(swInstallType)])
    
    if "times" in metafunc.fixturenames:
        times = metafunc.config.getoption("--times")
        metafunc.parametrize("times", range(int(times)))

