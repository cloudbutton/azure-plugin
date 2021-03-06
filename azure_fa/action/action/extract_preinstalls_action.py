#
# Copyright Cloudlab URV 2020
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import sys
import pkgutil
import json
import azure.functions as func
from azure.storage.queue import QueueService


def main(msgIn: func.QueueMessage, msgOut: func.Out[func.QueueMessage]):
    print("Extracting preinstalled Python modules...")
    runtime_meta = dict()
    mods = list(pkgutil.iter_modules())
    runtime_meta["preinstalls"] = [entry for entry in sorted([[mod, is_pkg] for _, mod, is_pkg in mods])]
    python_version = sys.version_info
    runtime_meta["python_ver"] = str(python_version[0])+"."+str(python_version[1])

    msgOut.set(json.dumps(runtime_meta))