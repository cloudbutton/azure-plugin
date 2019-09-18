import sys
from pywren_ibm_cloud.utils import version_str

RUNTIME_DEFAULT_35 = 'dhak/pywren-runtime-azure:v1.0.20'
RUNTIME_DEFAULT_36 = 'dhak/pywren-runtime-azure:v1.0.20'
RUNTIME_DEFAULT_37 = 'dhak/pywren-runtime-azure:v1.0.20'

RUNTIME_TIMEOUT_DEFAULT = 600000  # Default: 600000 milliseconds => 10 minutes
RUNTIME_TIMEOUT_MAX = 600000    # Platform maximum
RUNTIME_TIMEOUT_MIN  = 300000   # Platform minimum
RUNTIME_MEMORY_DEFAULT = 256  # Default memory: 256 MB


def load_config(config_data=None):
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

    required_parameters = ('resource_group', 'service_plan', 'account_name', 'docker_username')

    if set(required_parameters) > set(config_data['azure_fa']):
        raise Exception('You must provide {} to access to Azure Function App '\
                        .format(required_parameters))
