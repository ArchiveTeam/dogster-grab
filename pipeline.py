import datetime
from distutils.version import StrictVersion
import hashlib
import os
import seesaw
from seesaw.config import NumberConfigValue, StringConfigValue
from seesaw.externalprocess import WgetDownload
from seesaw.item import ItemInterpolation, ItemValue
from seesaw.pipeline import Pipeline
from seesaw.project import Project
from seesaw.task import SimpleTask, LimitConcurrent
from seesaw.tracker import (GetItemFromTracker, SendDoneToTracker,
    PrepareStatsForTracker, UploadWithTracker)
from seesaw.util import find_executable
import shutil
import socket
import sys
import time


# check the seesaw version
if StrictVersion(seesaw.__version__) < StrictVersion("0.1.5"):
    raise Exception("This pipeline needs seesaw version 0.1.5 or higher.")


###########################################################################
# Find a useful Wget+Lua executable.
#
# WGET_LUA will be set to the first path that
# 1. does not crash with --version, and
# 2. prints the required version string
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

if not WGET_LUA:
    raise Exception("No usable Wget+Lua found.")


###########################################################################
# The version number of this pipeline definition.
#
# Update this each time you make a non-cosmetic change.
# It will be added to the WARC files and reported to the tracker.
VERSION = "20140126.01"
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36'
TRACKER_ID = 'dogster'
TRACKER_HOST = 'tracker.archiveteam.org'


###########################################################################
# This section defines project-specific tasks.
#
# Simple tasks (tasks that do not need any concurrency) are based on the
# SimpleTask class and have a process(item) method that is called for
# each item.
class CheckIP(SimpleTask):
    def __init__(self, warc_prefix):
        SimpleTask.__init__(self, "CheckIP")
        self._counter = 0

    def process(self, item):
        # NEW for 2014! Check if we are behind firewall/proxy
        ip_str = socket.gethostbyname('dogster.com')
        if ip_str != '204.9.177.200':
            item.log_output('Got IP address: %s' % ip_str)
            item.log_output(
                'Are you behind a firewall/proxy? That is a big no-no!')
            item.fail()

        # Check only occasionally
        if self._counter <= 0:
            self._counter = 10
        else:
            self._counter -= 1


class PrepareDirectories(SimpleTask):
    def __init__(self, warc_prefix):
        SimpleTask.__init__(self, "PrepareDirectories")
        self.warc_prefix = warc_prefix
        StringConfigValue('dogster_joke',
            name='Dog or Cat Preference',
            description='Are you a dog or cat person?'
        )

    def process(self, item):
        item_name = item["item_name"]
        dirname = "/".join((item["data_dir"], item_name))

        if os.path.isdir(dirname):
            shutil.rmtree(dirname)

        os.makedirs(dirname)

        item["item_dir"] = dirname
        item["warc_file_base"] = "%s-%s-%s" % (self.warc_prefix, item_name,
            time.strftime("%Y%m%d-%H%M%S"))

        open("%(item_dir)s/%(warc_file_base)s.warc.gz" % item, "w").close()


class MoveFiles(SimpleTask):
    def __init__(self):
        SimpleTask.__init__(self, "MoveFiles")

    def process(self, item):
        # NEW for 2014! Check if wget was compiled with zlib support
        if os.path.exists("%(item_dir)s/%(warc_file_base)s.warc"):
            raise Exception('Please compile wget with zlib support!')

        os.rename("%(item_dir)s/%(warc_file_base)s.warc.gz" % item,
              "%(data_dir)s/%(warc_file_base)s.warc.gz" % item)

        shutil.rmtree("%(item_dir)s" % item)


def get_hash(filename):
    with open(filename, 'rb') as in_file:
        return hashlib.sha1(in_file.read()).hexdigest()


PIPELINE_SHA1 = get_hash(__file__)
DOGSTER_SHA1 = get_hash(os.path.join(os.path.dirname(__file__)), 'dogster.lua')
FLIQZ_SHA1 = get_hash(os.path.join(os.path.dirname(__file__)), 'fliqz.lua')


def stats_id_function(item):
    # NEW for 2014! Some accountability hashes and stats.
    return {
        'pipeline_hash': PIPELINE_SHA1,
        'dogster_hash': DOGSTER_SHA1,
        'fliqz_hash': FLIQZ_SHA1,
        'python_version': sys.version,
    }


class WgetArgs(object):
    def realize(self, item):
        wget_args = [
            WGET_LUA,
            "-U", ItemInterpolation("%(user_agent)s"),
            "-nv",
            "-o", ItemInterpolation("%(item_dir)s/wget.log"),
            "--lua-script", "dogster.lua",
            "--no-check-certificate",
            "--output-document", ItemInterpolation("%(item_dir)s/wget.tmp"),
            "--truncate-output",
            "-e", "robots=off",
            "--no-cookies",
            "--rotate-dns",
            "--recursive", "--level=inf",
            "--page-requisites",
            "--timeout", "60",
            "--tries", "inf",
            "--span-hosts",
            "--no-parent",
            "--waitretry", "3600",
            "--domains", "dogster.com,catster.com,cdnster.com,fliqz.com",
            "--warc-file",
                ItemInterpolation("%(item_dir)s/%(warc_file_base)s"),
            "--warc-header", "operator: Archive Team",
            "--warc-header", "dogster-dld-script-version: " + VERSION,
            "--warc-header", ItemInterpolation("dogster-user: %(item_name)s"),
        ]

        item_name = item['item_name']
        item_type, item_data = item_name.split(':', 1)

        item['item_type'] = item_type
        item['item_data'] = item_data

        if item_type == 'profile':
            profile_id = item_data
            wget_args.append('http://www.dogster.com/dogs/%s' % profile_id)
            wget_args.append('http://www.catster.com/cats/%s' % profile_id)
        else:
            raise Exception('Unknown item_type')

        if 'bind_address' in globals():
            wget_args.extend(['--bind-address', globals()['bind_address']])
            print('')
            print('*** Wget will bind address at {0} ***'.format(
                globals()['bind_address']))
            print('')

        return wget_args


downloader = globals()['downloader']  # quiet the code checker

###########################################################################
# Initialize the project.
#
# This will be shown in the warrior management panel. The logo should not
# be too big. The deadline is optional.
project = Project(
    title="Dogster/Catster Communities",
    project_html="""
    <img class="project-logo" alt="" src="http://archiveteam.org/images/6/65/Dogster_logo.jpg" height="50" />
    <h2>Dogster/Catster <span class="links">
        <a href="http://www.dogster.com/">Dogster Website</a> &middot;
        <a href="http://www.catster.com/">Catster Website</a> &middot;
        <a href="http://%s/%s/">Leaderboard</a></span></h2>
    <p><b>Dogster/Catster Communities</b> are put to sleep.</p>
    """ % (TRACKER_HOST, TRACKER_ID)
    , utc_deadline=datetime.datetime(2014, 01, 03, 00, 00, 1)
)

pipeline = Pipeline(
    GetItemFromTracker("http://%s/%s" % (TRACKER_HOST, TRACKER_ID), downloader,
        VERSION),
    PrepareDirectories(warc_prefix="dogster"),
    WgetDownload(
        WgetArgs(),
        max_tries=5,
        accept_on_exit_code=[0, 8],
        env={
            'item_type': ItemValue("item_type"),
            'item_data': ItemValue("item_data"),
            'item_dir': ItemValue("item_dir"),
        }
    ),
    PrepareStatsForTracker(
        defaults={"downloader": downloader, "version": VERSION},
        file_groups={
            "data": [ItemInterpolation("%(item_dir)s/%(warc_file_base)s.warc.gz")]
        },
        id_function=stats_id_function,
    ),
    MoveFiles(),
    LimitConcurrent(NumberConfigValue(min=1, max=4, default="1",
        name="shared:rsync_threads", title="Rsync threads",
        description="The maximum number of concurrent uploads."),
        UploadWithTracker(
            "http://%s/%s" % (TRACKER_HOST, TRACKER_ID),
            downloader=downloader,
            version=VERSION,
            files=[
                ItemInterpolation("%(data_dir)s/%(warc_file_base)s.warc.gz"),
                ItemInterpolation("%(data_dir)s/%(warc_file_base)s.friends")
                ],
            rsync_target_source_path=ItemInterpolation("%(data_dir)s/"),
            rsync_extra_args=[
                "--recursive",
                "--partial",
                "--partial-dir", ".rsync-tmp"
            ]
            ),
    ),
    SendDoneToTracker(
        tracker_url="http://%s/%s" % (TRACKER_HOST, TRACKER_ID),
        stats=ItemValue("stats")
    )
)
