#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Test application for immagescanner

from imagescanner import ImageScanner

iscanner = ImageScanner()
scanners = iscanner.list_scanners()

if scanners:
    scanner = scanners[0]
    picture = scanner.scan(300)
    im = picture.rotate(-90)
    im.save("imagescanner-test.png", "PNG", dpi=(300, 300))
else:
    print "Can not find any scanner!!!"