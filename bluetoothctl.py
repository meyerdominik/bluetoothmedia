import subprocess
import time


def scan(scan_timeout=20):
    p = subprocess.Popen(["bluetoothctl", "scan", "on"])
    time.sleep(scan_timeout)
    p.terminate()
    return __devices()


def __devices():
    devices_s = subprocess.check_output("bluetoothctl devices", shell=True).decode().split("\n")[:-1]
    devices = {}
    for each in devices_s:
        devices[each[7:24]] = each[25:]
    return devices


def info():
    return subprocess.check_output("bluetoothctl info", shell=True).decode()

def pair(mac_address):
    subprocess.check_output("bluetoothctl pair {}".format(mac_address), shell=True)

def trust(mac_address):
  subprocess.check_output("bluetoothctl trust {}".format(mac_address), shell=True)


def remove(mac_address):
    subprocess.check_output("bluetoothctl remove {}".format(mac_address), shell=True)


def connect(mac_address):
    subprocess.check_output("bluetoothctl connect {}".format(mac_address), shell=True)


def disconnect():
    subprocess.check_output("bluetoothctl disconnect", shell=True)


def paired_devices():
    return subprocess.check_output("bluetoothctl paired-devices", shell=True).decode()
