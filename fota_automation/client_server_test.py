import pytest
import subprocess
import os
import shutil

#def test_client():

#    assert True

    #deviceSN = "TEST-SWFOTA-A-1"
    #deviceType = "AURA"
#
    #server_folder_path = "D:/DeviceFolders/{0}_{1}/Server/Debug_x64".format(deviceSN, deviceType)
    #client_orig_folder_path = "D:/DeviceFolders/{0}_{1}/Client/Debug_x64".format(deviceSN, deviceType)
    #client_folder_path = "D:/Program Files/Lumenis/ClientWPF_Tester"
#
    ##with capsys.disabled():
    #print(server_folder_path)
    #print(client_orig_folder_path)
#
    ##shutil.rmtree(client_folder_path, onerror=remove_readonly)
    ##shutil.copytree(client_orig_folder_path, client_folder_path)
#
    #times = 1
#
    #server = subprocess.Popen([os.path.join(server_folder_path, "LumXServerHost.exe"), "{0}".format(times)], cwd="D:/DeviceFolders/TEST-SWFOTA-A-1_AURA/Server/Debug_x64/")
    #client = subprocess.Popen([os.path.join(client_folder_path, "ClientWPF_Tester.exe"), "{0}".format(times)], cwd="D:/DeviceFolders/TEST-SWFOTA-A-1_AURA/Client/Debug_x64/")