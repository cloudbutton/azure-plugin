import sys
import os
from pywren_ibm_cloud.utils import version_str

RUNTIME_DEFAULT_35 = 'pywren-runtime'
RUNTIME_DEFAULT_36 = 'pywren-runtime' #'dhak/azure-pywren-runtime:default' # 'mcr.microsoft.com/azure-functions/python:2.0' #'prova-sense'
RUNTIME_DEFAULT_37 = 'pywren-runtime'

RUNTIME_TIMEOUT_DEFAULT = 600000  # Default: 600000 milliseconds => 10 minutes
RUNTIME_TIMEOUT_MAX = 600000    # Platform maximum
RUNTIME_TIMEOUT_MIN  = 300000   # Platform minimum
RUNTIME_MEMORY_DEFAULT = 256  # Default memory: 256 MB

ACTION_MODULES_DIR = os.path.join('.python_packages', 'lib', 'site-packages')

def load_config(config_data=None):
    this_version_str = version_str(sys.version_info)
    if this_version_str != '3.6':
        raise Exception('The functions backend Azure Function Apps currently'
                        ' only supports Python version 3.6.X and the local Python'
                        'version is {}'.format(this_version_str))

    if 'runtime_memory' not in config_data['pywren']:
        config_data['pywren']['runtime_memory'] = RUNTIME_MEMORY_DEFAULT
    if 'runtime_timeout' not in config_data['pywren']:
        config_data['pywren']['runtime_timeout'] = RUNTIME_TIMEOUT_DEFAULT
    else:
        if config_data['pywren']['runtime_timeout'] > RUNTIME_TIMEOUT_MAX:
            config_data['pywren']['runtime_timeout'] = RUNTIME_TIMEOUT_MAX
        if config_data['pywren']['runtime_timeout'] < RUNTIME_TIMEOUT_MIN:
            config_data['pywren']['runtime_timeout'] = RUNTIME_TIMEOUT_MIN
    if 'runtime' not in config_data['pywren']:
        this_version_str = version_str(sys.version_info)
        if this_version_str == '3.5':
            config_data['pywren']['runtime'] = RUNTIME_DEFAULT_35
        elif this_version_str == '3.6':
            config_data['pywren']['runtime'] = RUNTIME_DEFAULT_36
        elif this_version_str == '3.7':
            config_data['pywren']['runtime'] = RUNTIME_DEFAULT_37

    if 'azure_fa' not in config_data:
        raise Exception("azure_fa section is mandatory in the configuration")

    required_parameters = ('resource_group', 'consumption_plan', 'account_name', 'account_key', 'docker_username')

    if set(required_parameters) > set(config_data['azure_fa']):
        raise Exception('You must provide {} to access to Azure Function App '\
                        .format(required_parameters))
