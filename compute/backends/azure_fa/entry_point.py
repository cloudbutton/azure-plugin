#
# (C) Copyright IBM Corp. 2018
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

import logging, json
import azure.functions as func
from pywren_ibm_cloud.runtime.function_handler.handler import function_handler
from pywren_ibm_cloud.config import cloud_logging_config

cloud_logging_config(logging.INFO)
logger = logging.getLogger('__main__')


def main(req: func.HttpRequest) -> func.HttpResponse:
    logger.info("Starting IBM Cloud Function execution")
    function_handler(req.get_json())
    return func.HttpResponse(
            '{"Execution": "Finished"}',
            status_code=400
    )
