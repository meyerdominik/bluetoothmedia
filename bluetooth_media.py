# imports
import os
import can
import dbus
import dbus.mainloop.glib
import bluetoothctl
import time
import struct

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

#DBus init
def DBusInit():
  global oBus
  global oBlueZ
  global oObjMgr

  dbus.mainloop.glib.DBusGMainLoop(set_as_default = True)
  oBus = dbus.SystemBus()
  oBlueZ = oBus.get_object('org.bluez', "/")
  oObjMgr = dbus.Interface(oBlueZ, 'org.freedesktop.DBus.ObjectManager')

# Can
def CanInit():
  global oCan

  os.system('sudo ip link set can0 type can bitrate ' + str(nCanBitrate))
  os.system('sudo ifconfig can0 up')
  os.system('sudo ip link set can1 type can bitrate ' + str(nCanBitrate))
  os.system('sudo ifconfig can1 up')
  oCan = can.interface.Bus(channel = sConnectedToCarCan, bustyp = 'socketcan_ctypes')

def DeInitCan():
  global oCan
  
  os.system('sudo ifconfig can0 down')
  os.system('sudo ifconfig can1 down')
  oCan = None


# MediaControls
def MediaControlsExists():
  global oMediaPlayerInterface 
  global oTransportInterface 
  global oBus
  global oObjMgr

  for path, ifaces in oObjMgr.GetManagedObjects().items():
    if 'org.bluez.MediaPlayer1' in ifaces:
      oMediaPlayerInterface = dbus.Interface(oBus.get_object('org.bluez', path), 'org.bluez.MediaPlayer1')
    elif 'org.bluez.MediaTransport1' in ifaces:
      oTransportInterface = dbus.Interface(oBus.get_object('org.bluez', path), 'org.freedesktop.DBus.Properties')

  if not oMediaPlayerInterface or not oTransportInterface:
    return False
  else:
    return True


def HandleMessage(msg):
  global oMediaPlayerInterface 
  global oTransportInterface 

  ByteStruct = ""
  for i in range(msg.dlc):
    ByteStruct = ByteStruct + "B"

  data = struct.unpack(ByteStruct, msg.data)

  # msg.arbitration_id, msg.data
  if msg.arbitration_id == 0:
    oMediaPlayerInterface.Play()
  elif msg.arbitration_id == 1: # TODO Herausfinden
    oMediaPlayerInterface.Pause()
  elif msg.arbitration_id == 2: # TODO Herausfinden
    oMediaPlayerInterface.Next()
  elif msg.arbitration_id == 3: # TODO Herausfinden
    oMediaPlayerInterface.Previous()
  elif msg.arbitration_id == 4: # TODO Herausfinden
    vol = int(data[0])
    if vol in range(0, 128): # 0-127 // 00-7F
      oTransportInterface.Set('org.bluez.MediaTransport1', 'Volume', dbus.UInt16(vol))


if __name__ == '__main__':
  DBusInit()
  while True:
    try:
      while not (bluetoothctl.something_connected() and MediaControlsExists()):
        macs = bluetoothctl.scan(5)
        bScanMeinHandyWarImRadius = False
        for mac in macs:
          
          # Sonderfaelle
          if mac == sBluetoothMACVonMeinemHandy:
            bScanMeinHandyWarImRadius = True
            if bMeinHandyWarImRadius:
              # Verbindung herstellen zu meinem Telefon, wenn es ausserhalb des Radius war
              bluetoothctl.connect(mac)
              bMeinHandyWarImRadius = True
              break
        
        bMeinHandyWarImRadius = bScanMeinHandyWarImRadius
        
        # warten
        time.sleep(1)

      CanInit()

      # Volume auf Max
      oTransportInterface.Set('org.bluez.MediaTransport1', 'Volume', dbus.UInt16(127))

      while (bluetoothctl.something_connected() and MediaControlsExists()):
        HandleMessage(oCan.recv())
      DeInitCan()

    except Exception as e:
      print 'Exception ' + str(e)
      DeInitCan()
      time.sleep(1)