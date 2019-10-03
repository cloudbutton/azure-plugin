import ssl
import json
import time
import logging
import requests
import http.client
import os, shutil
import subprocess as sp
import tempfile
from urllib.parse import urlparse


logger = logging.getLogger(__name__)
logger.setLevel(logging.CRITICAL)


class FunctionAppClient:

      def __init__(self, config):
            """
            Constructor
            """
            self.resource_group = config['resource_group']
            self.service_plan = config['service_plan']
            self.storage_account = config['account_name']

      def create_action(self, action_name, image_name, memory=None):

            cmd = 'az functionapp create --name {} --storage-account {} --resource-group {} --plan {} --deployment-container-image-name {}'\
                  .format(action_name, self.storage_account, self.resource_group, self.service_plan, image_name)
            child = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE) # silent
            child.wait()
            logger.error(child.stderr.read().decode())

            cmd = 'az storage account show-connection-string --resource-group {} --name {} --query connectionString --output tsv'\
                  .format(self.resource_group, self.storage_account)
            child = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
            child.wait()
            connString = child.stdout.read().decode()
            connString = connString.split('==')[0] + '==' # to get rid of the end of line char(s)
            logger.error(child.stderr.read().decode())

            cmd = 'az functionapp config appsettings set --name {} --resource-group {} --settings "AzureWebJobsDashboard={}" "AzureWebJobsStorage={}"'\
                  .format(action_name, self.resource_group, connString, connString)
            child = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE) # silent
            child.wait()
            logger.error(child.stderr.read().decode())

      def delete_action(self, action_name):
            """
            Delete an Azure Function App
            """
            cmd = 'az functionapp delete --name {} --resource-group {}'.format(action_name, self.resource_group)
            child = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE) # silent
            child.wait()
            logger.error(child.stderr.read().decode())

