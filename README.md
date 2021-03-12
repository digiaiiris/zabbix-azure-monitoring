# zabbix-azure-monitoring

This python module provides Zabbix monitoring support for Azure resources.




## Requirements

- Zabbix agent
- pip3
- adal (installed automatically as dependency)
- azure-identity (installed automatically as dependency)
- azure-mgmt-monitor (installed automatically as dependency)
- azure-mgmt-resource (installed automatically as dependency)
- msrestazure (installed automatically as dependency)
- requests (installed automatically as dependency)


## Installation

1. Install the python module using pip.

```
pip3 install https://github.com/digiaiiris/zabbix-azure-monitoring/releases/download/1.9.1/azure-monitoring-1.9.1.tar.gz
```

2. Copy the [Zabbix agent configuration](etc/zabbix/zabbix_agent.d/ic_azure.conf) to /etc/zabbix/zabbix_agent.d directory.

3. Restart the Zabbix agent.




## Usage

### Resource discovery

Item Syntax | Description | Units |
----------- | ----------- | ----- |
azure.discover.resources[configuration_file] | Discover resources from Azure's services | {#RESOURCE} |



### Metric discovery

Item Syntax | Description | Units |
----------- | ----------- | ----- |
azure.discover.metrics[configuration_file, resource] | Discover metrics from Azure's resources | {#METRIC_CATEGORY}, {#METRIC_NAME} |



### roleInstance and roleName discovery

Item Syntax | Description | Units |
----------- | ----------- | ----- |
azure.discover.roles[configuration_file, resource, metric_category/metric_name, dimension] | Discover roles from Azure's resources | {#ROLE_NAME} |



### Azure metrics

Item Syntax | Description | Units |
----------- | ----------- | ----- |
azure.metric[configuration_file, resource, metric_category/metric_name, statistic, timegrain] | Retrieve metrics from Azure's resources | Count, Percent, Milliseconds, Seconds, etc.
azure.metric.timeshift[configuration_file, resource, metric_category/metric_name, statistic, timegrain, timeshift] | Retrieve metrics from Azure's resources | Count, Percent, Milliseconds, Seconds, etc.



### Azure Kusto queries

Item Syntax | Description | Response |
----------- | ----------- | -------- |
azure.application.insights[configuration_file, application ID, query] | Run Kusto query to Application Insights REST API | JSON
azure.log.analytics[configuration_file, workspace ID, query] | Run Kusto query to Log Analytics REST API | JSON



### Azure Logic App queries

Item Syntax | Description | Response |
----------- | ----------- | -------- |
azure.logic.apps[configuration_file, resource_group] | Discover Azure Logic App workflows | {#WORKFLOW_ID}, {#WORKFLOW_NAME}
azure.logic.apps[configuration_file, resource_group, workflow_name] | Discover Azure Logic App workflow triggers | {#TRIGGER_ID}, {#TRIGGER_NAME}
azure.logic.apps[configuration_file, resource_group, workflow_name, trigger_name ] | Discover Azure Logic App workflow trigger history | {#HISTORY_ID}, {#HISTORY_NAME}, {#HISTORY_STATUS}



## Examples

### Example configuration file
```
{
    "client_id": "<client_id>",
    "subscription_id": "<subscription_id>",
    "pemfile": "<path_to_pem_file>",
    "tenant_id": "<tenant_id>",
    "thumbprint": "<pem_file_thumbprint>",
    "application_ids": {
        "<application_key_1>": "<application_id_1>",
        "<application_key_2>": "<application_id_2>",
        "<application_key_3>": "<application_id_3>"
    },
    "workspace_ids": {
        "<workspace_key_1>": "<workspace_id_1>",
        "<workspace_key_2>": "<workspace_id_2>",
        "<workspace_key_3>": "<workspace_id_3>"
    },
    "kusto_queries": {
        "<kusto_query_key_1>": "<kusto_query_1>",
        "<kusto_query_key_2>": "<kusto_query_2>",
        "<kusto_query_key_3>": "<kusto_query_3>"
    },
    "resources": {
        "<resource_key_1>": "<resource_path_1>",
        "<resource_key_2>": "<resource_path_2>",
        "<resource_key_3>": "<resource_path_3>"
    }
}
```



### PEM-file thumbprint can be retrieved using OpenSSL command
```
openssl x509 -in <path_to_pem_file> -fingerprint -noout
```



### List available resources from Azure's services
```
azure_discover_resources <path_to_config_file>
```



### List available metrics from resource
```
azure_discover_metrics <path_to_config_file> <resource>
```



### List available roleInstances and roleNames from resource
```
azure_discover_roles <path_to_config_file> <resource> <metric> <dimension>
```



### Retrieve metric from resource
```
azure_metric <path_to_config_file> <resource> <metric> <statistic> <timegrain> --timeshift <timeshift>
```



### Possible values for statistic-argument

Average, Count, Minimum, Maximum, Total



### Possible values for timegrain-argument
PT1M, PT1H, P1D
