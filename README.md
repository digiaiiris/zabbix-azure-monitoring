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
pip install https://github.com/digiaiiris/zabbix-azure-monitoring/releases/download/1.3.1/azure-monitoring-1.3.1.tar.gz
```

2. Copy the [Zabbix agent configuration](etc/zabbix/zabbix_agent.d/ic_azure.conf) to /etc/zabbix/zabbix_agent.d directory.

3. Restart the Zabbix agent.




## Usage

### Resource discovery

Item Syntax | Description | Units |
----------- | ----------- | ----- |
azure.discover.resources[configuration_file] | Discover resources from Azure's services | {#RESOURCE_GROUP}, {#COMPANY_PROVIDER_NAME}, {#RESOURCE_TYPE}, {#RESOURCE_NAME} |



### Metric discovery

Item Syntax | Description | Units |
----------- | ----------- | ----- |
azure.discover.metrics[configuration_file, resource_group, provider_name, resource_type, resource] | Discover metrics from Azure's resources | {#METRIC_CATEGORY}, {#METRIC_NAME} |



### Instance discovery

Item Syntax | Description | Units |
----------- | ----------- | ----- |
azure.discover.instances[configuration_file, resource_group, provider_name, resource_type, resource, metric_category/metric_name] | Discover instances from Azure's resources | {#INSTANCE_NAME} |



### Azure metrics

Item Syntax | Description | Units |
----------- | ----------- | ----- |
azure.metric[configuration_file, resource_group, provider_name, resource_type, resource, metric_category/metric_name, statistic, timegrain]' | Retrieve metrics from Azure's resources | Count, Percent, Milliseconds, Seconds, etc.
azure.metric.timeshift[configuration_file, resource_group, provider_name, resource_type, resource, metric_category/metric_name, statistic, timegrain, timeshift]' | Retrieve metrics from Azure's resources | Count, Percent, Milliseconds, Seconds, etc.



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



### List available resources from Azure's services
```
azure_discover_resources -c "<path_to_config_file>"
```



### List available metrics from resource
```
azure_discover_metrics -c "<path_to_config_file>" -g "<resource_group>" -p "<provider_name>" -t "<provider_type>" -r "<resource_name>"
```



### List available instances from resource
```
azure_discover_instances -c "<path_to_config_file>" -g "<resource_group>" -p "<provider_name>" -t "<provider_type>" -r "<resource_name>" "<metric>"
```



### Retrieve metric from resource
```
azure_metric -c "<path_to_config_file>" -g "<resource_group>" -p "<provider_name>" -t "<provider_type>" -r "<resource_name>" "<metric>" <statistic> <timegrain> --timeshift <timeshift>
```



### Possible values for statistic-argument

Average, Count, Minimum, Maximum, Total



### Possible values for timegrain-argument
PT1M, PT1H, P1D
