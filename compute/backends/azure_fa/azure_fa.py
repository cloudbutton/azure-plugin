import os
import sys
import logging
import shutil
import tempfile
import hashlib
import time
import json
import re
import subprocess as sp
import uuid
from . import config as azure_fa_config
from pywren_ibm_cloud.utils import version_str
from pywren_ibm_cloud.version import __version__
from pywren_ibm_cloud.libs.azure.functionapps_client import FunctionAppClient
from azure.storage.queue import QueueService
from azure.storage.queue.models import QueueMessageFormat
import pywren_ibm_cloud

logger = logging.getLogger(__name__)

class AzureFunctionAppBackend:
    """
    A wrap-up around Azure Function Apps backend.
    """

    def __init__(self, config):
        self.log_level = os.getenv('CB_LOG_LEVEL')
        self.name = 'azure_fa'
        self.azure_fa_config = config
        self.version = 'pywren_v'+__version__
        self.fa_client = FunctionAppClient(self.azure_fa_config)
        self.queue_service = QueueService(account_name=self.azure_fa_config['account_name'],
                                          account_key=self.azure_fa_config['account_key'])
        self.queue_service.encode_function = QueueMessageFormat.text_base64encode
        self.queue_service.decode_function = QueueMessageFormat.text_base64decode


        log_msg = 'PyWren v{} init for Azure Function Apps'.format(__version__)
        logger.info(log_msg)
        if not self.log_level:
            print(log_msg)

    def _format_action_name(self, action_name):
        sha_1 = hashlib.sha1()
        block = action_name.encode('ascii', errors='ignore')
        sha_1.update(block)
        tag = sha_1.hexdigest()[:8]

        sha_1 = hashlib.sha1()
        block = self.azure_fa_config['account_name'].encode('ascii', errors='ignore')
        sha_1.update(block)
        tag = tag + sha_1.hexdigest()[:8]
        
        version = re.sub(r'[/_:.]', '', __version__)
        action_name = action_name[:16] + '-' + version[:5] + '-' + tag

        return action_name

    def _format_queue_name(self, action_name, type):
        #  Using different queue names because there's a delay between deleting a queue   
        #  and creating another one with the same name
        return action_name + '-' + type

    def _create_runtime_custom(self, action_name, extract_preinstalls=False):
        """
        Creates a new runtime from a custom docker image
        """

        def add_base_modules():
            cmd = 'pip3 install --system -t {} -r requirements.txt'.format(azure_fa_config.ACTION_MODULES_DIR)
            os.system(cmd)

        def add_pywren_module(action_name):
            module_location = os.path.dirname(os.path.abspath(pywren_ibm_cloud.__file__))
            shutil.copytree(module_location, os.path.join(azure_fa_config.ACTION_MODULES_DIR, 'pywren_ibm_cloud'))

        def get_bindings_str(action_name, extract_preinstalls=False):
            if not extract_preinstalls:
                bindings = {
                    "scriptFile": "__init__.py",
                    "bindings": [
                        {
                            "name": "msgIn",
                            "type": "queueTrigger",
                            "direction": "in",
                            "queueName": self._format_queue_name(action_name, 'trigger'),
                            "connection": "AzureWebJobsStorage"
                        }
                    ]}
            else:
                bindings = {
                    "scriptFile": "__init__.py",
                    "bindings": [
                        {
                            "name": "msgIn",
                            "type": "queueTrigger",
                            "direction": "in",
                            "queueName": self._format_queue_name(action_name,
                                                                 type='trigger'),
                            "connection": "AzureWebJobsStorage"
                        },
                        {
                            "name": "msgOut",
                            "type": "queue",
                            "direction": "out",
                            "queueName": self._format_queue_name(action_name,
                                                                 type='result'),
                            "connection": "AzureWebJobsStorage"
                        }]}
            return json.dumps(bindings)

        initial_dir = os.getcwd()
        temp_folder = next(tempfile._get_candidate_names())
        os.mkdir(temp_folder)
        os.chdir(temp_folder)

        try:
            project_dir = os.path.join(initial_dir, temp_folder, action_name)
            action_dir = os.path.join(project_dir, action_name)

            # Create project folder from the template
            project_template = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'action')
            shutil.copytree(project_template, project_dir)
            os.chdir(project_dir)
            os.rename('action', action_dir)
            
            # Add the whole current pywren module
            os.makedirs(azure_fa_config.ACTION_MODULES_DIR, exist_ok=True)
            add_base_modules()
            add_pywren_module(action_name) 

            # Set entry point file
            if extract_preinstalls:
                entry_point_file = 'extract_preinstalls_action.py'
            else:
                entry_point_file = 'handler_action.py'

            os.rename(os.path.join(action_dir, entry_point_file), 
                        os.path.join(action_dir, '__init__.py'))

            # Edit the function's bindings for it to be a queue triggered function
            with open(os.path.join(action_dir, 'function.json'), 'w') as bindings_file:
                bindings_file.write(get_bindings_str(action_name, extract_preinstalls))
                
            # Create trigger queue, create action
            queue_name = self._format_queue_name(action_name, type='trigger')
            self.queue_service.create_queue(queue_name)
            self.fa_client.create_action(action_name)
            print('Created function:', action_name)

        except Exception as e:
            raise Exception("Unable to create the new runtime", e)
        finally: 
            os.chdir(initial_dir)
            #shutil.rmtree(temp_folder, ignore_errors=True) # Remove tmp project folder


    def get_unique_id(self):
        return str(uuid.uuid4()).replace('-', '')[:10]

    def create_runtime(self, docker_image_name, memory=None, timeout=azure_fa_config.RUNTIME_TIMEOUT_DEFAULT):

        unique_id = self.get_unique_id()
        metadata = self._generate_runtime_meta('pywren-extract-preinstalls-' + unique_id)
        # print(json.dumps(metadata))
        # with open('/home/pol/Desktop/azure/sleep_test/preinstalls.json') as f:
        #     metadata = json.loads(f.read())

        logger.info('Creating new PyWren runtime based on {}'.format(docker_image_name))
        self._create_runtime_custom(self._format_action_name(docker_image_name))

        return metadata

    def delete_runtime(self, docker_image_name, extract_preinstalls=False):
        """
        Deletes a runtime
        """

        action_name = self._format_action_name(docker_image_name)
        self.fa_client.delete_action(action_name)
        queue_name = self._format_queue_name(docker_image_name, type='trigger')
        self.queue_service.delete_queue(queue_name)

    def invoke(self, docker_image_name, memory=None, payload={}):
        """
        Invoke function
        """        
        exec_id = payload['executor_id']
        job_id = payload['job_id']
        call_id = payload['call_id']
        action_name = self._format_action_name(docker_image_name)
        queue_name = self._format_queue_name(action_name, type='trigger')
        start = time.time()
        print(json.dumps(payload))
        try:
            msg = self.queue_service.put_message(queue_name, json.dumps(payload))
            activation_id = msg.id
            roundtrip = time.time() - start
            resp_time = format(round(roundtrip, 3), '.3f')

            if activation_id is None:
                log_msg = ('ExecutorID {} | JobID {} - Function {} invocation failed'.format(exec_id, job_id, call_id))
                logger.debug(log_msg)
            else:
                log_msg = ('ExecutorID {} | JobID {} - Function {} invocation done! ({}s) - Activation ID: '
                        '{}'.format(exec_id, job_id, call_id, resp_time, activation_id))
                logger.debug(log_msg)
        except Exception:
            self.queue_service.create_queue(queue_name)
            return self.invoke(docker_image_name, memory=memory, payload=payload)

        return activation_id

    def invoke_with_result(self, docker_image_name, memory=None, payload={}):
        """
        Not doable on this implementation, which uses queues as a trigger to the function,
        and no response is expected after the call.
        """
        raise Exception('Cannot invoke_with_result() on this current '
                        'Azure Function App as a backend implementation')


    def _invoke_with_result(self, docker_image_name):
        result_queue_name = self._format_queue_name(docker_image_name, type='result')
        self.queue_service.create_queue(result_queue_name)
        trigger_queue_name = self._format_queue_name(docker_image_name, type='trigger')
        self.queue_service.put_message(trigger_queue_name, '')

        msg = []
        while not msg:
            msg = self.queue_service.get_messages(result_queue_name, num_messages=1)
            time.sleep(0.5)
        result_str = msg[0].content
        self.queue_service.delete_queue(result_queue_name)
        
        return json.loads(result_str)

    def get_runtime_key(self, docker_image_name, runtime_memory):
        """
        Method that creates and returns the runtime key.
        Runtime keys are used to uniquely identify runtimes within the storage,
        in order to know which runtimes are installed and which not.
        """
        action_name = self._format_action_name(docker_image_name)
        runtime_key = os.path.join(self.name, action_name)

        return runtime_key

    def _generate_runtime_meta(self, action_name):
        """
        Extract installed Python modules from docker image
        """

        self._create_runtime_custom(action_name, extract_preinstalls=True)

        logger.debug("Extracting Python modules list from Azure Linux host")
        try:
            print('Invoking extract metadata')
            runtime_meta = self._invoke_with_result(action_name)
        except Exception:
            raise Exception("Unable to invoke 'modules' action")
        try:
            self.delete_runtime(action_name, extract_preinstalls=True)
        except Exception:
            raise Exception("Unable to delete 'modules' action")

        if not runtime_meta or 'preinstalls' not in runtime_meta:
            raise Exception(runtime_meta)

        return runtime_meta
