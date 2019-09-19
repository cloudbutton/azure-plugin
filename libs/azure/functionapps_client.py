import ssl
import json
import time
import base64
import logging
import requests
import http.client
import os, shutil
import subprocess
import tempfile
from urllib.parse import urlparse


logger = logging.getLogger(__name__)


class FunctionAppClient:

    def __init__(self, config):
        """
        Constructor
        """
        self.resource_group = config['resource_group']
        self.service_plan = config['service_plan']
        self.storage_account = config['account_name']

        self.session = requests.session()

        self.headers = {
            'User-Agent': config['user_agent'],
            'Content-Type': 'application/json'
        }

        self.session.headers.update(self.headers)
        #adapter = requests.adapters.HTTPAdapter()
        #self.session.mount('https://', adapter)

    def create_action(self, action_name, image_name, memory=None,
                      timeout=30000):

        cmd = 'az functionapp create --name {} --storage-account {} --resource-group {} --plan {} --deployment-container-image-name {}'\
              .format(action_name, self.storage_account, self.resource_group, self.service_plan, image_name)
        os.system(cmd)

        cmd = 'az storage account show-connection-string --resource-group {} --name {} --query connectionString --output tsv'\
              .format(self.resource_group, self.storage_account)
        connString = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout
        connString = connString.read().decode()
        connString = connString.split('==')[0] + '==' # to get rid of the end of line char(s)

        cmd = 'az functionapp config appsettings set --name {} --resource-group {} --settings "AzureWebJobsDashboard={}" "AzureWebJobsStorage={}"'\
              .format(action_name, self.resource_group, connString, connString)
        os.system(cmd)

    # def get_action(self, package, action_name):
    #     """
    #     Get an IBM Cloud Functions action
    #     """
    #     logger.debug("I am about to get a cloud function action: {}".format(action_name))
    #     url = '/'.join([self.endpoint, 'api', 'v1', 'namespaces', self.effective_namespace, 'actions', package, action_name])
    #     res = self.session.get(url)
    #     return res.json()

    # def list_actions(self, package):
    #     """
    #     List all IBM Cloud Functions actions in a package
    #     """
    #     logger.debug("I am about to list all actions from: {}".format(package))
    #     url = '/'.join([self.endpoint, 'api', 'v1', 'namespaces', self.effective_namespace, 'actions', package, ''])
    #     res = self.session.get(url)
    #     return res.json()

    def delete_action(self, action_name):
        """
        Delete an Azure Function App
        """
        cmd = 'az functionapp delete --name {} --resource-group {}'.format(action_name, self.resource_group)
        os.system(cmd)

    # def update_memory(self, package, action_name, memory):
    #     logger.debug('I am about to update the memory of the {} action to {}'.format(action_name, memory))
    #     url = '/'.join([self.endpoint, 'api', 'v1', 'namespaces', self.effective_namespace,
    #                     'actions', package, action_name + "?overwrite=True"])

    #     data = {"limits": {"memory": memory}}
    #     res = self.session.put(url, json=data)
    #     resp_text = res.json()

    #     if res.status_code != 200:
    #         logger.debug('An error occurred updating action {}: {}'.format(action_name, resp_text['error']))
    #     else:
    #         logger.debug("OK --> Updated action memory {}".format(action_name))

    # def list_packages(self):
    #     """
    #     List all IBM Cloud Functions packages
    #     """
    #     logger.debug('I am about to list all the IBM CF packages')
    #     url = '/'.join([self.endpoint, 'api', 'v1', 'namespaces', self.effective_namespace, 'packages'])

    #     res = self.session.get(url)

    #     if res.status_code == 200:
    #         return res.json()
    #     else:
    #         logger.debug("Unable to list packages")
    #         raise Exception("Unable to list packages")

    # def delete_package(self, package):
    #     """
    #     Delete an IBM Cloud Functions package
    #     """
    #     logger.debug("I am about to delete the package: {}".format(package))
    #     url = '/'.join([self.endpoint, 'api', 'v1', 'namespaces', self.effective_namespace, 'packages', package])
    #     res = self.session.delete(url)
    #     resp_text = res.json()

    #     if res.status_code == 200:
    #         return resp_text
    #     else:
    #         logger.debug('An error occurred deleting the package {}: {}'.format(package, resp_text['error']))

    # def create_package(self, package):
    #     """
    #     Create an IBM Cloud Functions package
    #     """
    #     logger.debug('I am about to create the package {}'.format(package))
    #     url = '/'.join([self.endpoint, 'api', 'v1', 'namespaces', self.effective_namespace, 'packages', package + "?overwrite=False"])

    #     data = {"name": package}
    #     res = self.session.put(url, json=data)
    #     resp_text = res.json()

    #     if res.status_code != 200:
    #         logger.debug('Package {}: {}'.format(package, resp_text['error']))
    #     else:
    #         logger.debug("OK --> Created package {}".format(package))

    def invoke(self, url, payload={}):
        resp = self.session.post(url, data=json.dumps(payload))
        
        return resp.json()
