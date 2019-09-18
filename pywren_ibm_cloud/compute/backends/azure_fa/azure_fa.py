import os
import sys
import logging
import shutil
import tempfile
import hashlib
import time
from . import config as azure_fa_config
from pywren_ibm_cloud.utils import version_str
from pywren_ibm_cloud.version import __version__
from pywren_ibm_cloud.libs.azure.functionapps_client import FunctionAppClient
import pywren_ibm_cloud
import azure.functions as func

logger = logging.getLogger(__name__)


class AzureFunctionAppBackend:
    """
    A wrap-up around Azure Function Apps backend.
    """

    def __init__(self, azure_fa_config):
        self.log_level = os.getenv('CB_LOG_LEVEL')
        self.name = 'azure_fa'
        self.azure_fa_config = azure_fa_config
        self.version = 'pywren_v'+__version__
        self.fa_client = FunctionAppClient(self.azure_fa_config)

        log_msg = 'PyWren v{} init for Azure Function Apps'
        logger.info(log_msg)
        if not self.log_level:
            print(log_msg)

    def _format_action_name(self, runtime_name):
        runtime_name = runtime_name.replace('/', '-').replace(':', '-')

        sha_1 = hashlib.sha1()
        block = runtime_name.encode('ascii', errors='ignore')
        sha_1.update(block)
        tag = sha_1.hexdigest()[:8]

        sha_1 = hashlib.sha1()
        block = self.azure_fa_config['account_name'].encode('ascii', errors='ignore')
        sha_1.update(block)
        tag = tag + sha_1.hexdigest()[:8]
        
        return runtime_name[:16] + tag

    def _unformat_action_name(self, action_name):
        runtime_name, memory = action_name.rsplit('_', 1)
        image_name = runtime_name.replace('_', '/', 1)
        image_name = image_name.replace('_', ':', -1)
        return image_name, int(memory.replace('MB', ''))
    
    def _get_default_runtime_image_name(self):
        this_version_str = version_str(sys.version_info)
        if this_version_str == '3.5':
            image_name = azure_fa_config.RUNTIME_DEFAULT_35
        elif this_version_str == '3.6':
            image_name = azure_fa_config.RUNTIME_DEFAULT_36
        elif this_version_str == '3.7':
            image_name = azure_fa_config.RUNTIME_DEFAULT_37
        return image_name
    
    def _edit_dockerfile_image(self, docker_image_name):
        with open('Dockerfile', 'r') as df:
            lines = df.read().splitlines()

        with open('Dockerfile', 'w') as df:
            i = 0
            for line in lines:
                if line[0:4] == 'FROM':
                    break
                else:
                    i = i+1
            lines[i] = 'FROM {}'.format(docker_image_name)
            for line in lines: 
                df.write(line)
                df.write(os.linesep)

    def _add_requirements(self):
        current_location = os.path.dirname(os.path.abspath(__file__))
        pywren_req = os.path.join(current_location, 'requirements.txt')
        action_req = os.path.join(os.getcwd(), 'requirements.txt')
        shutil.copyfile(pywren_req, action_req)

    def _rm_project (self, initial_dir, temp_folder):
        os.chdir(initial_dir)
        shutil.rmtree(temp_folder, ignore_errors=True)

    def build_runtime(self, docker_image_name, dockerfile='Dockerfile'):
        """
        Builds a new runtime from a Docker file and pushes it to the Docker hub
        """
        logger.info('Creating a new docker image from Dockerfile')
        logger.info('Docker image name: {}'.format(docker_image_name))

        cmd = 'docker build -t {} -f {} .'.format(docker_image_name, dockerfile)

        res = os.system(cmd)
        if res != 0:
            exit()

        cmd = 'docker push {}'.format(docker_image_name)
        res = os.system(cmd)
        if res != 0:
            exit()

    def _create_runtime_custom(self, docker_image_name, extract_preinstalls=False):
        """
        Creates a new runtime from a custom docker image
        """
        initial_dir = os.getcwd()
        temp_folder = next(tempfile._get_candidate_names())
        os.mkdir(temp_folder)
        os.chdir(temp_folder)

        action_name = self._format_action_name(docker_image_name)
        cmd = 'func init {} --docker --worker-runtime python'.format(action_name)
        os.system(cmd)
        os.chdir(action_name)
        cmd = 'func new --name {} --template "HttpTrigger"'.format(action_name)
        os.system(cmd)

        current_location = os.path.dirname(os.path.abspath(__file__))
        if extract_preinstalls:
            action_location = os.path.join(current_location, 'extract_preinstalls_action.py')
        else:
            action_location = os.path.join(current_location, 'entry_point.py')

        entry_point_location = os.path.join(os.getcwd(), action_name, '__init__.py')
        shutil.copyfile(action_location, entry_point_location)
        
        self._edit_dockerfile_image(docker_image_name)
        self._add_requirements()

        logger.info('Creating new PyWren runtime based on Docker image {}'.format(docker_image_name))

        action_image_name = '{}/functionapp:{}'.format(self.azure_fa_config['docker_username'], action_name[-16:])
        self.build_runtime(action_image_name)
        self.fa_client.create_action(action_name, action_image_name)

        os.chdir(initial_dir)
        #self._rm_project(initial_dir, temp_folder)

    def _create_runtime_default(self):
        docker_image_name = self._get_default_runtime_image_name()
        action_name = self._format_action_name(docker_image_name)
        logger.info('Creating new PyWren runtime based on Docker image {} (default)'.format(docker_image_name))
        self.fa_client.create_action(action_name, docker_image_name)

    def create_runtime(self, docker_image_name, memory=None, timeout=azure_fa_config.RUNTIME_TIMEOUT_DEFAULT):
        if docker_image_name == 'default':
            self._create_runtime_default()
        else:
            self._create_runtime_custom(docker_image_name)

    def delete_runtime(self, docker_image_name):
        """
        Deletes a runtime
        """
        if docker_image_name == 'default':
            docker_image_name = self._get_default_runtime_image_name()
        action_name = self._format_action_name(docker_image_name)
        self.fa_client.delete_action(action_name)

    # def delete_all_runtimes(self):
    #     """
    #     Deletes all runtimes from all packages
    #     """
    #     packages = self.cf_client.list_packages()
    #     for pkg in packages:
    #         if 'pywren_v' in pkg['name']:
    #             actions = self.cf_client.list_actions(pkg['name'])
    #             while actions:
    #                 for action in actions:
    #                     self.cf_client.delete_action(pkg['name'], action['name'])
    #                 actions = self.cf_client.list_actions(pkg['name'])
    #             self.cf_client.delete_package(pkg['name'])

    # def list_runtimes(self, docker_image_name='all'):
    #     """
    #     List all the runtimes deployed in the IBM CF service
    #     return: list of tuples [docker_image_name, memory]
    #     """
    #     if docker_image_name == 'default':
    #         docker_image_name = self._get_default_runtime_image_name()
    #     runtimes = []
    #     actions = self.cf_client.list_actions(self.package)

    #     for action in actions:
    #         action_image_name, memory = self._unformat_action_name(action['name'])
    #         if docker_image_name == action_image_name or docker_image_name == 'all':
    #             runtimes.append([action_image_name, memory])
    #     return runtimes

    def invoke(self, docker_image_name, memory=None, payload={}):
        """
        Invoke -- return information about this invocation
        """
        exec_id = payload['executor_id']
        job_id = payload['job_id']
        call_id = payload['call_id']
        action_name = self._format_action_name(docker_image_name)
        start = time.time()

        # --- TODO: get the endpoint using Azure Active Directory
        activation_id = self.fa_client.invoke(
            input('(2) Action endpoint: '),
            payload)
        # ---
        roundtrip = time.time() - start
        resp_time = format(round(roundtrip, 3), '.3f')

        if activation_id is None:
            log_msg = ('ExecutorID {} | JobID {} - Function {} invocation failed'.format(exec_id, job_id, call_id))
            logger.debug(log_msg)
        else:
            log_msg = ('ExecutorID {} | JobID {} - Function {} invocation done! ({}s) - Activation ID: '
                       '{}'.format(exec_id, job_id, call_id, resp_time, activation_id))
            logger.debug(log_msg)

        return activation_id

    def invoke_with_result(self, docker_image_name, memory=None, payload={}):
        return self.fa_client.invoke(
            input('(1) Action endpoint: '),
            payload)

    def get_runtime_key(self, docker_image_name, runtime_memory):
        """
        Method that creates and returns the runtime key.
        Runtime keys are used to uniquely identify runtimes within the storage,
        in order to know which runtimes are installed and which not.
        """
        action_name = self._format_action_name(docker_image_name)
        runtime_key = os.path.join(self.name, action_name)

        return runtime_key

    def generate_runtime_meta(self, docker_image_name):
        """
        Extract installed Python modules from docker image
        """
        if docker_image_name == 'default':
            docker_image_name = self._get_default_runtime_image_name()

        # old_stdout = sys.stdout
        # sys.stdout = open(os.devnull, 'w')
        try:
            self._create_runtime_custom(docker_image_name, extract_preinstalls=True)
        except Exception as e:
            raise e
        # sys.stdout = old_stdout
        logger.debug("Extracting Python modules list from: {}".format(docker_image_name))
        try:
            runtime_meta = self.invoke_with_result(docker_image_name)
        except Exception:
            raise Exception("Unable to invoke 'modules' action")
        try:
            self.delete_runtime(docker_image_name)
        except Exception:
            raise Exception("Unable to delete 'modules' action")

        if not runtime_meta or 'preinstalls' not in runtime_meta:
            raise Exception(runtime_meta)

        return runtime_meta