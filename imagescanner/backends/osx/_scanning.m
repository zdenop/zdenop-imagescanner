
#import <Carbon/Carbon.h>
#include <Python/Python.h>


const char* getStringValue(NSDictionary* dict, NSString* key)
{
    return [[dict objectForKey:key] UTF8String];
}


unsigned long int getNumericValue(NSDictionary* dict, NSString* key)
{
    return [[dict objectForKey:key] unsignedLongValue];
}


PyObject* getListOfStringsValue(NSDictionary* dict, NSString* key)
{
    NSArray *array = [dict objectForKey:key];
    Py_ssize_t i;
    Py_ssize_t len = [array count];
    PyObject *list = PyList_New(len);    
    for (i = 0; i < len; ++i) {
        PyObject *item = PyString_FromString([[array objectAtIndex:i] UTF8String]);
        NSCAssert(item != NULL, @"Can't add NULL item to Python List");
        PyList_SetItem(list, i, item);
    }
    return list;
}


PyObject* devicePropertyDictToPyObject(NSDictionary* devicePropertyDict)
{        
    return Py_BuildValue("{s:s,s:s,s:s,s:s,s:s,s:s,s:n,s:n,s:n,s:O}",
        "name", getStringValue(devicePropertyDict, @"ifil"),
        "serial_number",  getStringValue(devicePropertyDict, 
                                         @"ICADeviceSerialNumberString"),
        "type", getStringValue(devicePropertyDict, @"ICADeviceTypeKey"),
        "user_custom_name", getStringValue(devicePropertyDict,
                                           @"ICAUserAssignedDeviceNameKey"),
        "session_status",  getStringValue(devicePropertyDict, 
                                          @"scannerSessionStatus"),
        "uuid", getStringValue(devicePropertyDict, @"UUIDString"),
        "id", getNumericValue(devicePropertyDict, @"icao"),
        "idProduct", getNumericValue(devicePropertyDict, @"idProduct"),
        "idVendor", getNumericValue(devicePropertyDict, @"idVendor"),
        "resolutions", getListOfStringsValue(devicePropertyDict, 
                                             @"preferred resolutions")
    );
}


PyObject* deviceListToPyObject(NSArray *devices)
{
    // Cast the devices List to pyobject
    Py_ssize_t i;
    Py_ssize_t len = [devices count];
    PyObject *py_devices = PyList_New(len);
    
    for (i = 0; i < len; ++i) {
        PyObject *item = devicePropertyDictToPyObject([devices objectAtIndex:i]);
        NSCAssert(item != NULL, @"Can't add NULL item to Python List");
        PyList_SetItem(py_devices, i, item);
    }
    
    return py_devices;
}


PyObject* getDeviceList(PyObject *self, PyObject *args)
{
    ICAGetDeviceListPB  deviceList_pb = {};
    ICACopyObjectPropertyDictionaryPB deviceListPropDict_pb = {};
    NSDictionary* deviceListPropDict = NULL;
    NSArray* devices;
    OSErr err;
    
    // get the device list pb
    err = ICAGetDeviceList(&deviceList_pb, NULL);
    if (err != noErr) return NULL;
    
    // load the device list property dict pb
    deviceListPropDict_pb.object = deviceList_pb.object;
    deviceListPropDict_pb.theDict = (CFDictionaryRef*)(&deviceListPropDict);
    err = ICACopyObjectPropertyDictionary( &deviceListPropDict_pb, NULL );
    if (err != noErr) return NULL;
    
    // get the device list
    devices = [deviceListPropDict objectForKey:@"devices"];

    return deviceListToPyObject(devices);    
}

static PyMethodDef scanningMethods[] = {
    {"getDeviceList", getDeviceList, METH_VARARGS, "TODO"},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC init_scanning(void)
{
    (void) Py_InitModule("_scanning", scanningMethods);
    
    // mac os black magic: this is needed in order to get
    //    garbage collection working properly
    [[NSAutoreleasePool alloc] init];
}
