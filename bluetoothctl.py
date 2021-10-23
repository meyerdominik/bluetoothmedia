import subprocess
from sys import stdout
import time

class Device:
    sMAC = ''
    bConnected = False

def scan(scan_timeout = 20):
    aRtn = list()
    p = subprocess.Popen(["bluetoothctl", "scan", "on"], stdout=subprocess.PIPE)
    time.sleep(scan_timeout)
    p.terminate()

    lines = p.stdout.read().splitlines()
    for line in lines:
        splitted = line.split(' ')
        if splitted[1] == "Device":
            aRtn.append(splitted[2])
            
    return aRtn

def info(mac_address):
    return subprocess.check_output("bluetoothctl info {}".format(mac_address), shell = True).decode()

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

def pair(mac_address):
    p = subprocess.Popen("bluetoothctl pair {}".format(mac_address), shell = True)
    p.wait()

def trust(mac_address):
    p = subprocess.Popen("bluetoothctl trust {}".format(mac_address), shell = True)
    p.wait()

def trusted(mac_address):
    bRtn = False
    lines = subprocess.check_output("bluetoothctl info {}".format(mac_address), shell = True).decode().splitlines()

    for line in lines:
        if line.__contains__("Trusted: "):
            bRtn = line.__contains__("yes")
    return bRtn


def remove(mac_address):
    p = subprocess.Popen("bluetoothctl remove {}".format(mac_address), shell = True)
    p.wait()


def connect(mac_address):
    p = subprocess.Popen("bluetoothctl connect {}".format(mac_address), shell = True)
    p.wait()


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