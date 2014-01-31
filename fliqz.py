#!/usr/bin/env python
'''Given a Fliqz video id, return the URL of the flv file.

A simple port of
https://github.com/monsieurvideo/get-flash-videos/blob/master/lib/FlashVideo/Site/Fliqz.pm

If you are reading this docstring, please feel my pain.
(SOAP?! You've got to be kidding me...)

Anyway, please check out http://archiveteam.org/index.php?title=Dev
'''
from __future__ import print_function

import re
import sys
import time
import urllib2


XML = '''<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<SOAP-ENV:Body>
  <i0:ad xmlns:i0="urn:fliqz.s.mac.20071201">
  <i0:rq>
    <i0:a>{0}</i0:a>
    <i0:pu></i0:pu>
    <i0:pid>1F866AF1-1DB0-4864-BCA1-6236377B518F</i0:pid>
  </i0:rq>
</i0:ad>
</SOAP-ENV:Body>
</SOAP-ENV:Envelope>'''


def main(video_id):
    # Hi. Please don't try to refactor this (even though it's so~~~ tempting).
    # Instead, help us write *new* scripts in the future. Thanks!

    url = 'http://services.fliqz.com/mediaassetcomponentservice/20071201/service.svc'
    headers = {
        'Content-Type': "text/xml; charset=utf-8",
        'SOAPAction': '"urn:fliqz.s.mac.20071201/IMediaAssetComponentService/ad"',
        'Referer': 'http://rawdogster.web'
    }

    post_data = XML.format(video_id)

    request = urllib2.Request(url, post_data, headers)
    response = urllib2.urlopen(request)
    content = response.read()

    match = re.search(r'>(http:[^<]+\.flv)<', content)

    if match:
        print(match.group(1))
        return

    url = 'http://services.fliqz.com/LegacyServices/Services/MediaAsset/Component/R20071201/service.svc'
    headers = {
        'Content-Type': "text/xml; charset=utf-8",
        'SOAPAction': '"urn:fliqz.s.mac.20071201/IMediaAssetComponentService/ad"',
        'Referer': 'http://rawdogster.web'
    }

    post_data = XML.format(video_id)

    request = urllib2.Request(url, post_data, headers)
    response = urllib2.urlopen(request)
    content = response.read()

    match = re.search(r'>(http:[^<]+\.flv)<', content)

    if match:
        print(match.group(1))
        return

    sys.exit('No video found!')


if __name__ == '__main__':
    video_id = sys.argv[1]

    for dummy in xrange(2000):
        try:
            print('un-fliqzing video_id', video_id, file=sys.stderr)
            main(video_id)
        except urllib2.HTTPError as error:
            print('un-fliqzing error', error, file=sys.stderr)
            time.sleep(60)

    print('un-fliqzing gave up.', file=sys.stderr)
