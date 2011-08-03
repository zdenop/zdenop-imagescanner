"""ImageScanner XMLRPC library. 

Runs a server which provide some of the library features on the network.

"""

import json
import xmlrpclib
from cStringIO import StringIO
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

from imagescanner import ImageScanner


def scanner_serializer(device):
    return {
        'id': device.id,
        'name': device.name,
        'manufacturer': getattr(device, 'manufacturer', None),
        'description': getattr(device, 'description', None),
    }


def list_scanners():
    devices = ImageScanner(remote_search=False).list_scanners()
    serialized_devices = [scanner_serializer(device) for device in devices]
    return json.dumps(serialized_devices)


def scan(device_id):
    image = ImageScanner(remote_search=False).scan(device_id)
    if image is None:
        return None
    image_data = StringIO()
    image.save(image_data, 'tiff')
    image_data.seek(0) 
    return xmlrpclib.Binary(image_data.read())

    
class RequestHandler(SimpleXMLRPCRequestHandler):
     rpc_paths = ('/RPC2',)


def run(listen_address, port):
    server = SimpleXMLRPCServer((listen_address, port), 
                                requestHandler=RequestHandler)

    server.register_introspection_functions()
    server.register_function(list_scanners)
    server.register_function(scan)
    server.serve_forever()
