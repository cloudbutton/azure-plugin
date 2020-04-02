# CloudButton Microsoft Azure Plugin
Cloudbutton toolkit plugin for Azure Function Apps and Azure Blob Storage.

- CloudButton Project: [http://cloudbutton.eu/](http://cloudbutton.eu/)
- CloudButton Toolkit: [https://github.com/pywren/pywren-ibm-cloud](https://github.com/pywren/pywren-ibm-cloud)

## Requirements

 - [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
 - [pip](https://pypi.org/project/pip/) (updated)
 
## Plugin setup

If you haven't installed `pywren-ibm-cloud` yet, you first have to [install](https://github.com/pywren/pywren-ibm-cloud/blob/master/README.md#pywren-setup) it.\
Assuming you already have installed PyWren:

  1. Clone this repository.
  2. Execute the `install_plugin.py` script. 
```
  python3 install_plugin.py
```
  3. Edit your local pywren config file (typically ~/.pywren_config)
     with the new parameters for Azure.\
     See [config_tempate.yaml](/config_template.yaml)
```yaml
  azure_blob:
    account_name : <STORAGE_ACCOUNT_NAME>
    account_key : <STORAGE_ACCOUNT_KEY>

  azure_fa:
    resource_group : <RESOURCE_GROUP>
    location : <CONSUMPTION_PLAN_LOCATION>
    account_name : <STORAGE_ACCOUNT_NAME>
    account_key : <STORAGE_ACCOUNT_KEY>
    functions_version : <AZURE_FUNCTIONS_VERSION>
```
   - `account_name`: the name of the Storage Account itself.
   - `account_key`: an Account Key, found in *Storage Account* > `account_name` > *Settings* > *Access Keys*.
   - `resource_group`: the Resource Group of your Storage Account. *Storage Account* > `account_name` > *Overview*.
   - `locatoin`: the location of the consumption plan for the runtime. \
      Use `az functionapp list-consumption-locations` to view available locations.
   - `functions_version`: optional, the Azure Functions runtime version (2 or 3).
      
      In addition, you have to specify a container that will be used internally by PyWren, and you have indicate that you want PyWren to use Azure Storage / Functions:     
```yaml
  pywren:
    storage_bucket: <CONTAINER_NAME>
    storage_backend : azure_blob
    compute_backend : azure_fa
```
  4. Sign in with Azure CLI:
```
  az login
```
  5. Use PyWren in your Python code.
  
Note: the first time executing it will take several minutes to deploy the runtime. If you want to see more information about the process, you can enable logging by passing the argument `pywren.function_executor(log_level='INFO')`.
