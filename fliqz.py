#!/usr/bin/env python
'''Given a Fliqz video id, return the URL of the flv file.

A simple port of
https://github.com/monsieurvideo/get-flash-videos/blob/master/lib/FlashVideo/Site/Fliqz.pm

If you are reading this docstring, please feel my pain.
(SOAP?! You've got to be kidding me...)

Anyway, please check out http://archiveteam.org/index.php?title=Dev
'''
from __future__ import print_function

import hashlib
import os.path
import re
from seesaw.util import find_executable
import subprocess
import sys
import time
import urllib2


VERSION = '20140201.01'

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


class NoVideoError(Exception):
    pass


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
        return True

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
        return True

    raise NoVideoError("No video found!")


WGET_LUA = find_executable(
    "Wget+Lua",
    ["GNU Wget 1.14.lua.20130523-9a5c"],
    [
        "./wget-lua",
        "./wget-lua-warrior",
        "./wget-lua-local",
        "../wget-lua",
        "../../wget-lua",
        "/home/warrior/wget-lua",
        "/usr/bin/wget-lua"
    ]
)


def run_wget(url, video_id, dirpath):
    wget_args = [
        WGET_LUA,
        "-U", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.73.11 (KHTML, like Gecko) Version/7.0.1 Safari/537.73.11",
        "-nv",
        "-o", os.path.join(
            dirpath, "wget_video_{0}.log".format(video_id)
        ),
        "--no-check-certificate",
        "--output-document", os.path.join(
            dirpath, "wget_video_{0}.tmp".format(video_id)
        ),
        "--truncate-output",
        "-e", "robots=off",
        "--no-cookies",
        "--rotate-dns",
        "--timeout", "60",
        "--tries", "2000",
        "--waitretry", "3600",
        "--warc-file", os.path.join(
            dirpath, "video.{0}.{1}".format(video_id, hashlib.sha1(url).hexdigest()[:6])
        ),
        "--warc-header", "operator: Archive Team",
        "--warc-header", "dogster-fliqz-dld-script-version: " + VERSION,
        "--warc-header", "dogster-video-id: {0}".format(video_id),
        "--header", "Content-Type: text/xml; charset=utf-8",
        "--header", 'SOAPAction: "urn:fliqz.s.mac.20071201/IMediaAssetComponentService/ad"',
        '--referer', 'http://rawdogster.web',
        '--method', 'POST',
        '--body-data', XML.format(video_id),
        url
    ]

    subprocess.call(wget_args)


if __name__ == '__main__':
    video_id = sys.argv[1]
    dirpath = sys.argv[2]

    for dummy in xrange(2000):
        try:
            print('un-fliqzing video_id', video_id, file=sys.stderr)
            if main(video_id):
                break
        except urllib2.HTTPError as error:
            print('un-fliqzing error', error, file=sys.stderr)
            time.sleep(60)
        except NoVideoError:
            print('No video found', file=sys.stderr)
            time.sleep(60)

    print("fliqzing wget", file=sys.stderr)
    run_wget(
        'http://services.fliqz.com/mediaassetcomponentservice/20071201/service.svc',
        video_id, dirpath
    )
    run_wget(
        'http://services.fliqz.com/LegacyServices/Services/MediaAsset/Component/R20071201/service.svc',
        video_id, dirpath
    )

    print('un-fliqzing done.', file=sys.stderr)
