# CloudButton Microsoft Azure Plugin
Cloudbutton toolkit plugin for Azure Function Apps and Azure Blob Storage.

- CloudButton Project: [http://cloudbutton.eu](http://cloudbutton.eu)
- CloudButton Toolkit: [https://github.com/cloudbutton/cloudbutton](https://github.com/cloudbutton/cloudbutton)

## Requirements

 - [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
 - [pip](https://pypi.org/project/pip/) (updated)
 - azure-storage-blob 2.1.0 (`pip install azure-storage-blob==2.1.0`)
 - azure-storage-queue 2.1.0 (`pip install azure-storage-queue==2.1.0`)
 
## Plugin setup

If you did not install `cloudbutton` yet, you first have to [install](https://github.com/cloudbutton/cloudbutton) it.\
Assuming you already have installed Cloudbutton:

  1. Clone this repository.
  2. Execute the `install_plugin.py` script. 
```
  python3 install_plugin.py
```
  3. Edit your local Cloudbutton config file (typically ~/.cloudbutton_config)
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
   - `location`: the location of the consumption plan for the runtime. \
      Use `az functionapp list-consumption-locations` to view available locations.
   - `functions_version`: optional, the Azure Functions runtime version (2 or 3, defaults to 2).
      
      In addition, you have to specify the container that will be used internally by Cloudbutton, and you have set that you want Cloudbutton to use Azure Storage / Functions:     
```yaml
  cloudbutton:
    storage_bucket: <CONTAINER_NAME>
    storage_backend : azure_blob
    compute_backend : azure_fa
```
  4. Sign in with Azure CLI:
```
  az login
```
  5. Use Cloudbutton toolkit in your Python code.
  
Note: the first time executing it will take several minutes to deploy the runtime. If you want to see more information about the process, you can set the log level to 'INFO'.
