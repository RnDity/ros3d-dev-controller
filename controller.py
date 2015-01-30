import sys 
import dbus
import tornado.web
import tornado.ioloop
from traceback import print_exc
from tornado.escape import json_encode, json_decode
import json
import gobject
import time
from dbus.mainloop.glib import DBusGMainLoop
from threading import Thread
from functools import wraps
import signal

#PARAMETERS 
class ParameterStatus:
    def __init__(self):
        self.read = True
        self.write = True
        self.statusType = "hardware"

class DoubleParameter:
    def __init__(self, name, value, valueType):
        self.name = name
        self.value = value
        self.valueType = valueType
        self.status = ParameterStatus()
        self.minValue = sys.float_info.min
        self.maxValue = sys.float_info.max

#INSTANCES
focusDistanceParam = DoubleParameter("focus_distance_m", 6.0, "float")
apertureParam = DoubleParameter("aperture", 30.0, "float")

#DBUS
DBUS_SERVO_SERIVCE = 'pl.ros3d.servo'
DBUS_SERVO_OBJECT = '/pl/ros3d/servo'
DBUS_SERVO_INTERFACE = 'pl.ros3d.servo'

class DBusHandler:

    busInterface = 0

    def connect(self, service, object, interface):
        print("DBusHandler init()")
        try:
            bus = dbus.SystemBus()
            busObject = bus.get_object(service, object)
        except dbus.DBusException:
            print("DBusHandler connect() failed")
            print_exc()
            exitApp()
        self.busInterface = dbus.Interface(busObject, interface)
        bus.add_signal_receiver(self.valueChanged, "valueChanged", interface)
        self.syncData()

    def syncData(self):
        apertureParam.value = self.getValue(apertureParam.name)
        focusDistanceParam.value = self.getValue(focusDistanceParam.name)

    def valueChanged(self,  parameter, motor_status, limit_status, in_progress_status, value):
        print("DBusHandler valueChanged() parameter %s" % parameter)
        print("DBusHandler valueChanged() value %f" % value)
        if(focusDistanceParam.name == parameter):
            print("DBusHandler valueChanged() focusDistance changed")
            focusDistanceParam.value = value
        if(apertureParam.name == parameter):
            print("DBusHandler valueChanged() aperteure changed")
            apertureParam.value = value

    def getValue(self, parameter):
        print("DBusHandler getValue()")
        return float(self.busInterface.getValue(parameter))

    def setValue(self, parameter, value):
        print("DBusHandler setValue()")
        self.busInterface.setValue(parameter, value)

    def calibrate(self, parameter):
        print("DBusHandler calibrate()")
        self.busInterface.calibrate(parameter)

    def isConnected(self):
        print("DBusHandler isConnected()")
        return self.busInterface.isConnected()

dbusApplication = DBusHandler()

#HELPERS
def runAsync(func):
    @wraps(func)
    def async_func(*args, **kwargs):
        func_hl = Thread(target=func, args=args, kwargs=kwargs)
        func_hl.start()
        return func_hl

    return async_func

def getIpAddress(interface):
    print("getIpAddress()")
    ip = "not_implemented"
    return ip

def updateApertureValue(value):
    print("updateApertureValue() value %f" % value)
    dbusApplication.setValue(apertureParam.name, dbus.Double(value))
    print("updateApertureVale() value setted, update from hardware now")
    apertureParam.value = dbusApplication.getValue(apertureParam.name)
    print("updateApertureValue() newValue %f" % apertureParam.value)


def updateFocusDistanceValue(value):
    print("updateFocusDistanceValue() value %f" % value)
    dbusApplication.setValue(focusDistanceParam.name, dbus.Double(value))
    print("updateFocusDistanceValue() value setted, update from hardware now")
    focusDistanceParam.value = dbusApplication.getValue(focusDistanceParam.name)
    print("updateFocusDistanceValue() newValue %f" % focusDistanceParam.value)

def calibrateServos():
    dbusApplication.calibrate(apertureParam.name)

def isServoConnected():
    return dbusApplication.isConnected()

#JSON
version = "1.0"
interface = "eth0"

versionJson = {
    "version":version
}

statusJson = {
    "camera_id":"A",
    "ip":getIpAddress(interface)
}

def parametersListJson():
    return {
        apertureParam.name: {
            "type" : apertureParam.valueType,
            "value" : apertureParam.value,
            "status" : {
                "read" : apertureParam.status.read,
                "write" : apertureParam.status.write,
                "type" : apertureParam.status.statusType
            }
        },
        focusDistanceParam.name: {
            "type" : focusDistanceParam.valueType,
            "value" : focusDistanceParam.value,
            "status" : {
                "read" : focusDistanceParam.status.read,
                "write" : focusDistanceParam.status.write,
                "type" : focusDistanceParam.status.statusType
            }
        }
    }

class SystemVersionHandler(tornado.web.RequestHandler):
    def get(self):
        print("SystemVersionHandler()")
        print("SystemVersionHandler() Response: %s" % json_encode(versionJson))
        self.write("%s" % json_encode(versionJson))            

class SystemStatusHandler(tornado.web.RequestHandler):
    def get(self):
        print("SystemStatusHandler()")
        print("SystemStatusHandler() Response: %s" % json_encode(statusJson))
        self.write("%s" % json_encode(statusJson))

class ParametersListHandler(tornado.web.RequestHandler):
    def get(self):
        print("ParametersListHandler()")
        print("ParametersListHandler() Response: %s" % parametersListJson())
        self.write("%s" % json_encode(parametersListJson()))

class ParametersUpdateHandler(tornado.web.RequestHandler):
    def put(self):
        print("ParametersUpdateHandler()")
        valueKey = "value"
        json = json_decode(self.request.body)
        print("ParametersUpdateHandler() Request: %s" % json)

        if(apertureParam.name in json):
            print("ParametersUpdateHandler() apertureParam exists")
            updateApertureValue(json[apertureParam.name][valueKey])
        
        if(focusDistanceParam.name in json):
            print("ParametersUpdateHandler() focusDistanceParam exists")
            updateFocusDistanceValue(json[focusDistanceParam.name][valueKey])
        
        self.write("%s" % json_encode(parametersListJson()))

class ServosCalibrateHandler(tornado.web.RequestHandler):
    def get(self):
        print("ServosCalibrateHandler()")
        calibrateServos()
        self.write("True")

class ServosConnectedHandler(tornado.web.RequestHandler):
    def get(self):
        print("ServosCalibrateHandler()")
        isConnected = isServoConnected()
        if(isConnected == 1):
	    self.write("True")
	else:
	    self.write("False")
       

webApplication = tornado.web.Application([
    (r"/api/system/version", SystemVersionHandler),
    (r"/api/system/status", SystemStatusHandler),
    (r"/api/parameters/list", ParametersListHandler),
    (r"/api/parameters/update", ParametersUpdateHandler),
    (r"/api/servo/calibrate", ServosCalibrateHandler),
    (r"/api/servo/connected", ServosConnectedHandler),
])

@runAsync
def startTornado():
    print("startTornado")
    webApplication.listen(80)
    tornado.ioloop.IOLoop.instance().start()

def stopTornado():
    print("stopTornado")
    tornado.ioloop.IOLoop.instance().stop()

@runAsync
def startDbus():
    print("startDbus")
    dbus.mainloop.glib.DBusGMainLoop(set_as_default = True)
    dbusApplication.connect(DBUS_SERVO_SERIVCE, DBUS_SERVO_OBJECT, DBUS_SERVO_INTERFACE)

def initParameters():
    print("initParameters")
    apertureParam.value = dbusApplication.getValue(apertureParam.name)
    focusDistanceParam.value = dbusApplication.getValue(focusDistanceParam.name)

def startApp():
    print("startApp")
    startTornado()
    startDbus()

def exitApp():
    print("exitApp")
    stopTornado();
    sys.exit(0)

def exitSignalHandler(signal, frame):
    print("exitSignalHandler")
    exitApp();

if __name__ == "__main__":
    
    gobject.threads_init()
    
    startApp()
    signal.signal(signal.SIGINT, exitSignalHandler)

    loop = gobject.MainLoop()
    loop.run()   
