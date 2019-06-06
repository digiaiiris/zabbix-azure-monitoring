# zabbix-azure-monitoring

This python module provides Zabbix monitoring support for Azure resources.




## Requirements

- Zabbix agent
- pip
- adal (installed automatically as dependency)
- azure (installed automatically as dependency)




## Installation

1. Install the python module using pip.

```
pip install https://github.com/digiaiiris/zabbix-azure-monitoring/releases/download/1.1.0/azure-monitoring-1.1.0.tar.gz
```

2. Copy the [Zabbix agent configuration](etc/zabbix/zabbix_agent.d/ic_azure.conf) to /etc/zabbix/zabbix_agent.d directory.

3. Restart the Zabbix agent.




## Usage

### Discovery

Item Syntax | Description | Units |
----------- | ----------- | ----- |
azure.discover[configuration_file, resource_group, provider_name, resource_type, resource] | Discover metrics from Azure resources | {#METRIC_CATEGORY}, {#METRIC_NAME} |



### Azure Metrics

Item Syntax | Description | Units |
----------- | ----------- | ----- |
azure.metric.timeshift[configuration_file, resource_group, provider_name, resource_type, resource, metric_category/metric_name, statistic, timegrain, timeshift]' | Retrieve metric from Azure resources | Count, Percent, Milliseconds, Seconds, etc.




## Retrieving available resources

Available resources can be retrieved using the Azure CLI application.



### Download and install the Azure CLI

https://docs.microsoft.com/en-us/cli/azure/install-azure-cli



### Authenticate using the Azure CLI
```
az login --service-principal -u "<subscription_id>" -p "<path_to_pem_file>" --tenant "<tenant_id>"
```



### List available resources using Azure CLI

`az resource list`




## Examples

### Example configuration file
```
{
    "application_id": "<application_id>",
    "subscription_id": "<subscription_id>",
    "pemfile": "<path_to_pem_file>",
    "tenant_id": "<tenant_id>",
    "thumbprint": "<pem_file_thumbprint>"
}
```



### PEM-file thumbprint can be retrieved using OpenSSL command
```
openssl x509 -in <path_to_pem_file> -fingerprint -noout
```



### List available metrics from resource
```
azure_discovery -c "<path_to_config_file>" -g "<resource_group>" -p "<provider_name>" -t "<provider_type>" -r "<resource_name>"
```



### Retrieve metric
```
azure_metric -c "<path_to_config_file>" -g "<resource_group>" -p "<provider_name>" -t "<provider_type>" -r "<resource_name>" "<metric>" <statistic> <timegrain> --timeshift <timeshift>
```



### Possible values for statistic-argument

Average, Count, Minimum, Maximum, Total



### Possible values for timegrain-argument
PT1M, PT1H, P1D
