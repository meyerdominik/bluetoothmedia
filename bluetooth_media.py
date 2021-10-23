# imports
import os
import can
import dbus
import dbus.mainloop.glib
import sys
#from gi.repository import GLib

# Variablen zum aendern
nCanBitrate = 100000
sConnectedToCarCan = 'can0' # oder can1

# NICHT ZUM AENDERN
# Vars
oCan = None
oMediaPlayerInterface = None
oTransportInterface = None

oBus = None
oBluez = None
oObjMgr = None

# init dbus
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
oBus = dbus.SystemBus()
oBlueZ = oBus.get_object('org.bluez', "/")
oObjMgr = dbus.Interface(oBlueZ, 'org.freedesktop.DBus.ObjectManager')

# canbus init
os.system('sudo ip link set can0 type can bitrate ' + str(nCanBitrate))
os.system('sudo ifconfig can0 up')

os.system('sudo ip link set can1 type can bitrate ' + str(nCanBitrate))
os.system('sudo ifconfig can1 up')

oCan = can.interface.Bus(channel = sConnectedToCarCan, bustyp = 'socketcan_ctypes')

while True:
  for path, ifaces in oObjMgr.GetManagedObjects().items():
    if 'org.bluez.MediaPlayer1' in ifaces:
      oMediaPlayerInterface = dbus.Interface(oBus.get_object('org.bluez', path), 'org.bluez.MediaPlayer1')
    elif 'org.bluez.MediaTransport1' in ifaces:
      oTransportInterface = dbus.Interface(oBus.get_object('org.bluez', path), 'org.freedesktop.DBus.Properties')

  if not oMediaPlayerInterface or not oTransportInterface:
    # Wenn eins nicht vorhanden ist, wird abgebrochen
    continue

  msg = oCan.recv()
