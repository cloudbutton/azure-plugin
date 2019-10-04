# CloudButton Microsoft Azure Plugin
Cloudbutton toolkit plugin for Azure Function Apps and Azure Blob Storage.

- CloudButton Project: [http://cloudbutton.eu/](http://cloudbutton.eu/)
- CloudButton Toolkit: [https://github.com/pywren/pywren-ibm-cloud](https://github.com/pywren/pywren-ibm-cloud)

## Requirements
 - [Azure Functions Core Tools](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local)
 - [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
 - [Docker](https://docs.docker.com/install/)
## Plugin setup
If you haven't installed `pywren-ibm-cloud` yet, you first have to [install](https://github.com/pywren/pywren-ibm-cloud/blob/master/README.md#pywren-setup) it.\
Assuming you already have installed PyWren:
  1.  Clone this repository.
  2.  Execute the `install_plugin.py` script. 
  ```
      python3 install_script.py
  ```
  3.  Edit your local pywren config file (typically ~/.pywren_config)
     with the new parameters for Azure.\
     See [config_tempate.yaml](/config_template.yaml)
     ```yaml
      azure_blob:
        account_name : <AZURE_STORAGE_ACCOUNT_NAME>
        account_key  : <AZURE_STORAGE_ACCOUNT_KEY>
        
      azure_fa:
        resource_group: <AZURE_RESOURCE_GROUP>
        service_plan: <AZURE_SERVICE_PLAN>
        account_name : <AZURE_STORAGE_ACCOUNT_NAME>
        account_key  : <AZURE_STORAGE_ACCOUNT_KEY>
        docker_username : <DOCKER_USERNAME>
     ```
      - `account_name`: The name of the Storage Account itself.
      - `account_key`: An account key. Found in *Storage Account* > *\*account_name\** > *Settings* > *Access Keys*.
      - `resource_group`: The resource group of your Storage Account. *Storage Account* > *\*account_name\** > *Overview*.
      - `service_plan`: The service plan / subscription to Azure. Found in *All Resources*.
      - `docker_username`: A Docker username, internally used to push new runtimes.
      
      In addition, you must indicate that you want PyWren to use Azure Storage / Functions:     
     ```yaml
        pywren:
          storage_backend: azure_blob
          compute_backend: azure_fa
     ```
     
     

