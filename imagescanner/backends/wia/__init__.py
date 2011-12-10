""" Windows Image Acquisition Automation Layer (WIA) backend.

$Id$"""

# TODO(zdenop): get properties
# TODO(zdenop): do we need to close device?

import win32com.client
import logging
import Image
from StringIO import StringIO

from imagescanner.backends import base

# Some of WIA Constants
WIA_DEVICE_MANAGER = "WIA.DeviceManager"
WIA_DEVICE_SCANNER = 1
WIA_IMG_FORMAT_BMP = "{B96B3CAB-0728-11D3-9D7B-0000F81EF32E}"
WIA_COMMAND_TAKE_PICTURE = "{AF933CAC-ACAD-11D2-A093-00C04F72DC3C}"

class ScannerManager(base.ScannerManager):
    """WIA Scanner manager"""
    
    def _refresh(self):
        """Get list of active devices"""
        self._devices = []

        devman = win32com.client.Dispatch(WIA_DEVICE_MANAGER)
        for dev in devman.DeviceInfos:
            # ignore other devices than scanners
            if dev.Type == WIA_DEVICE_SCANNER:
                scanner_id = 'wia-%s' % len(self._devices)
                try:
                    scanner = Scanner(scanner_id,
                        dev.Properties["Unique Device ID"],
                        dev.Properties["Manufacturer"],
                        dev.Properties["Name"],
                        dev.Properties["Description"])
                    self._devices.append(scanner)
                except Exception, err:
                    logging.exception(err)

class Scanner(base.Scanner):
    """WIA Scanner actions"""

    def __init__(self, scanner_id, device, manufacturer, name, description):
        super(Scanner, self).__init__()
        self.id = scanner_id
        self.manufacturer = manufacturer
        self.name = name
        self.description = description
        self._device = device

    def __repr__(self):
        return '<%s: %s - %s>' % (self.id, self.manufacturer, self.name)

    def scan(self, dpi = 300):
        # Find scanner
        logging.info('Scanning with WIA')
        devman = win32com.client.Dispatch(WIA_DEVICE_MANAGER)
        dev = None

        for info in devman.DeviceInfos:
            for prop in info.Properties:
                logging.debug("'%s':'%s'", prop.Name, str(prop.Value))
                if prop.Name == 'Name' and str(prop.Value) == str(self.name):
                    logging.info('Connecting to %s...', self.name)
                    dev = info.Connect()

        if not dev:
            logging.info('Can not connect to device \'%s\'! Quiting...',
                self.name)
            return None

        # Get a image
        for command in dev.Commands:
            if command.CommandID == WIA_COMMAND_TAKE_PICTURE:
                dev.ExecuteCommand(WIA_COMMAND_TAKE_PICTURE)

        try:
            dev.Items[dev.Items.Count].Properties["Horizontal Resolution"] = dpi
            dev.Items[dev.Items.Count].Properties["Vertical Resolution"] = dpi
        except Exception, err:
            logging.info('Cannot set DPI')
            logging.exception(err)

        image = dev.Items[dev.Items.count].Transfer(WIA_IMG_FORMAT_BMP)
        return Image.open(StringIO(image.FileData.BinaryData))

    def status(self):
        pass