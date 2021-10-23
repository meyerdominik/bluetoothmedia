import subprocess
import time

class Device:
    sMAC = ''
    bConnected = False

def scan(scan_timeout = 20):
    p = subprocess.Popen(["bluetoothctl", "scan", "on"])
    time.sleep(scan_timeout)
    p.terminate()
    return __devices()


def __devices():
    aRtn = list()
    lines = subprocess.check_output("bluetoothctl devices | cut -f2 -d' ' | while read uuid; do bluetoothctl info $uuid; done | grep -e \"Device\\|Connected\"", shell = True).decode().splitlines()

    nCurrentLine = -1

    for line in lines: 
        nCurrentLine += 1

        if line.startswith('Device'):
            sNextLine = lines[nCurrentLine + 1]
            NewDevice = Device()
            NewDevice.sMAC = line.split(' ')[1]
            if sNextLine.split(': ')[1] == "yes":
                NewDevice.bConnected = True
            elif sNextLine.split(': ')[1] == "no":
                NewDevice.bConnected = False
            aRtn.append(NewDevice)
    return aRtn


def info():
    return subprocess.check_output("bluetoothctl info", shell = True).decode()

def pair(mac_address):
    subprocess.check_output("bluetoothctl pair {}".format(mac_address), shell = True)

def trust(mac_address):
  subprocess.check_output("bluetoothctl trust {}".format(mac_address), shell = True)


def remove(mac_address):
    subprocess.check_output("bluetoothctl remove {}".format(mac_address), shell = True)


def connect(mac_address):
    subprocess.check_output("bluetoothctl connect {}".format(mac_address), shell = True)


def disconnect():
    subprocess.check_output("bluetoothctl disconnect", shell = True)


def paired_devices():
    return subprocess.check_output("bluetoothctl paired-devices", shell = True).decode()

def something_connected():
    bRtn = False
    for device in __devices():
        if device.bConnected:
            bRtn = True
            break
    
    return bRtn