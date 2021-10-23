# imports
import os
import can
import dbus
import dbus.mainloop.glib
import bluetoothctl
import time

# Variablen zum aendern
nCanBitrate = 100000
sConnectedToCarCan = 'can0' # oder can1
sBluetoothMACVonMeinemHandy = 'AC:D6:18:1C:ED:4C'

# NICHT ZUM AENDERN
# Vars
oCan = None
oMediaPlayerInterface = None
oTransportInterface = None

oBus = None
oBluez = None
oObjMgr = None

bMeinHandyWarImRadius = False
sLetzteMac = ''
bBluetoothConnected = False

# MediaControls
def MediaControlsExists():
  for path, ifaces in oObjMgr.GetManagedObjects().items():
    if 'org.bluez.MediaPlayer1' in ifaces:
      oMediaPlayerInterface = dbus.Interface(oBus.get_object('org.bluez', path), 'org.bluez.MediaPlayer1')
    elif 'org.bluez.MediaTransport1' in ifaces:
      oTransportInterface = dbus.Interface(oBus.get_object('org.bluez', path), 'org.freedesktop.DBus.Properties')

  if not oMediaPlayerInterface or not oTransportInterface:
    return False
  else:
    return True


# DBus init
dbus.mainloop.glib.DBusGMainLoop(set_as_default = True)
oBus = dbus.SystemBus()
oBlueZ = oBus.get_object('org.bluez', "/")
oObjMgr = dbus.Interface(oBlueZ, 'org.freedesktop.DBus.ObjectManager')

while True:
  try:
    while not (bluetoothctl.something_connected() and MediaControlsExists()):
      time.sleep(1)

    # Init Can
    os.system('sudo ip link set can0 type can bitrate ' + str(nCanBitrate))
    os.system('sudo ifconfig can0 up')
    os.system('sudo ip link set can1 type can bitrate ' + str(nCanBitrate))
    os.system('sudo ifconfig can1 up')
    oCan = can.interface.Bus(channel = sConnectedToCarCan, bustyp = 'socketcan_ctypes')
    
    while (bluetoothctl.something_connected() and MediaControlsExists()):
      msg = oCan.recv()
      print msg

    # Deinit Can  
    os.system('sudo ifconfig can0 down')
    os.system('sudo ifconfig can1 down')
    oCan = None

  except Exception as e:
    print 'Exception ' + str(e)
    
    # Deinit Can  
    os.system('sudo ifconfig can0 down')
    os.system('sudo ifconfig can1 down')
    oCan = None

    time.sleep(1)