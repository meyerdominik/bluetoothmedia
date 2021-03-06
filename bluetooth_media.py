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

bNoKeysPressed = True # Doppelte Nachrichten abfangen

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
  # https://www.loopybunny.co.uk/CarPC/can/1D6.html
  global oMediaPlayerInterface 
  global oTransportInterface 
  global bNoKeysPressed

  ByteStruct = ""
  for i in range(msg.dlc):
    ByteStruct = ByteStruct + "B"

  data = struct.unpack(ByteStruct, msg.data)

  # msg.arbitration_id, msg.data
  if msg.arbitration_id == 470: # 0x1D6
    if len(data) >= 2:
      if data[0] == 0xC0 and data[1] == 0x0C:
        bNoKeysPressed = True
      elif data[0] == 0xE0 and data[1] == 0x0C and bNoKeysPressed: # Up Button
        oMediaPlayerInterface.Next()
        bNoKeysPressed = False
      elif data[0] == 0xD0 and data[1] == 0x0C and bNoKeysPressed: # Down Button
        oMediaPlayerInterface.Previous()
        bNoKeysPressed = False
      elif data[0] == 0xC0 and data[1] == 0x0D and bNoKeysPressed: # Voice button
        oMediaPlayerInterface.Play()
        bNoKeysPressed = False
      elif data[0] == 0xC1 and data[1] == 0x0C and bNoKeysPressed: # Telephone Button
        oMediaPlayerInterface.Pause()
        bNoKeysPressed = False


if __name__ == '__main__':
  DBusInit()
  while True:
    try:
      while not (bluetoothctl.something_connected() and MediaControlsExists()):
        # Der Pi kann sich nicht von selbst aus verbinden... warum auch immer... 
        # TODO
        #
        #macs = bluetoothctl.scan(5)
        #bScanMeinHandyWarImRadius = False
        #for mac in macs:
        #  # Sonderfaelle
        #  if mac == sBluetoothMACVonMeinemHandy:
        #    bScanMeinHandyWarImRadius = True
        #    if not bMeinHandyWarImRadius:
        #      # Verbindung herstellen zu meinem Telefon, wenn es ausserhalb des Radius war
        #      bluetoothctl.connect(mac)
        #      bScanMeinHandyWarImRadius = True
        #      break
        #
        #if bMeinHandyWarImRadius and not bScanMeinHandyWarImRadius:
        #  bMeinHandyWarImRadius = False
        
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