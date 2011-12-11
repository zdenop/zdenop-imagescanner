"""Twain backend.

$Id$"""

import logging
from StringIO import StringIO

import win32com.client
import Image
import twain
from imagescanner.backends import base

class ScannerManager(base.ScannerManager):
    """Twain Scanner manager"""

    def _refresh(self):
        self._devices = []
        src_manager = twain.SourceManager(0)
        devices = src_manager.GetSourceList()
        # Creates list of installed devices. Devices cound not be available.

        # WIA help
        wia_devman = win32com.client.Dispatch("WIA.DeviceManager")
        available = list()
        for wia_dev in wia_devman.DeviceInfos:
        # Ignore other devices than scanners
            if wia_dev.Type == 1:
                available.append(str(wia_dev.Properties["Name"]))

        for dev in devices:
            # Test if scanner is available will open dialogue for each devices
            # regardless if it is available or not which is annoying on system
            # with a lot of installed devices...
            # http://stackoverflow.com/questions/100284/
            # how-do-i-check-if-the-scanner-is-plugged-in-c-net-twain
            # So lets cheat with WIA if device is available.
            #
            # TODO: make it depended on settings
            if dev.replace(' TWAIN','') in available:
                # twain added ' TWAIN' to name e.g. 'Canon DR-2580C TWAIN'
                scanner_id = 'twain-%s' % len(self._devices)
                try:
                    scanner = Scanner(scanner_id, dev)
                    self._devices.append(scanner)
                except Exception, exc:
                    # FixMe: What should be here?
                    # Debuging to try to find out
                    logging.debug(exc)
        src_manager.destroy()

class Scanner(base.Scanner):
    """WIA Scanner actions"""

    def __init__(self, scanner_id, source_name):
        super(Scanner, self).__init__()
        self.id = scanner_id
        self._source_name = source_name

        self.name = None
        self.manufacturer = None
        self.description = None
        self._src_manager = None
        self._scanner = None

        self._open()
        self._get_identity()
        self._close()

    def _get_identity(self):
        """Get information about scanner producer"""
        identity = self._scanner.GetIdentity()
        self.name = identity.get('ProductName')
        self.manufacturer = identity.get('Manufacturer')
        self.description = None

    def _open(self):
        """Open scanner for scanning"""
        self._src_manager = twain.SourceManager(0)
        self._scanner = self._src_manager.OpenSource(self._source_name)
        self._scanner.SetCapability(twain.ICAP_YRESOLUTION,
                                    twain.TWTY_FIX32, 200.0)

    def __repr__(self):
        return '<%s: %s - %s>' % (self.id, self.manufacturer, self.name)

    def scan(self, dpi=200):
        self._open()
        self._scanner.RequestAcquire(0, 0)
        info = self._scanner.GetImageInfo()
        if info:
            (handle, more_to_come) = self._scanner.XferImageNatively()
            str_image = twain.DIBToBMFile(handle)
            twain.GlobalHandleFree(handle)
            self._close()
            return Image.open(StringIO(str_image))

        self._close()
        return None

    def _close(self):
        """Close scanner"""
        self._scanner.destroy()
        self._src_manager.destroy()

    def status(self):
        pass
