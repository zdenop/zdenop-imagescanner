"""OS X backend."""

import _scanning

from imagescanner.backends import base 

class ScannerManager(base.ScannerManager):
 
    def _refresh(self):
        self._devices = [] 
        
        devices = _scanning.getDeviceList() 
        for dev in devices:
            scanner_id = 'osx-%s' % dev.get('id')
            name = dev.get('user_custom_name')

            scanner = Scanner(scanner_id, name, dev)
            self._devices.append(scanner)


class Scanner(base.Scanner):  
    def __init__(self, scanner_id, name, properties):
        self.id = scanner_id
        self.name = name
        self.properties = properties

    def __repr__(self):
        return '<%s: %s>' % (self.id, self.name)
 
