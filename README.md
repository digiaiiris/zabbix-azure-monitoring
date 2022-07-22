# zabbix-azure-monitoring

This python module provides Zabbix monitoring support for Azure resources.



## Requirements

- Zabbix agent
- pip3
- azure-identity (installed automatically as dependency)
- azure-mgmt-monitor (installed automatically as dependency)
- azure-mgmt-resource (installed automatically as dependency)
- msal (installed automatically as dependency)
- msrest (installed automatically as dependency)
- pyOpenSSL (installed automatically as dependency)
- requests (installed automatically as dependency)



## Installation

1. Install the python module using pip.

```
pip3 install https://github.com/digiaiiris/zabbix-azure-monitoring/releases/download/1.12.0/azure-monitoring-1.12.0.tar.gz
```

2. Copy the [Zabbix agent configuration](etc/zabbix/zabbix_agent.d/ic_azure.conf) to /etc/zabbix/zabbix_agent.d directory.

3. Restart the Zabbix agent.


---


## Usage

### Resource discovery

Item Syntax | Description | Units |
----------- | ----------- | ----- |
azure.discover.resources[configuration_file] | Discover resources from Azure's services | {#RESOURCE} |



### Metric discovery

Item Syntax | Description | Units |
----------- | ----------- | ----- |
azure.discover.metrics[configuration_file, resource] | Discover metrics from Azure's resources | {#METRIC_CATEGORY}, {#METRIC_NAME} |
azure.discover.metrics.namespace[configuration_file, resource, metric namespace] | Discover metrics from Azure's resources using metric namespace. | {#METRIC_CATEGORY}, {#METRIC_NAME} |



### Dimension discovery

Item Syntax | Description | Units |
----------- | ----------- | ----- |
azure.discover.dimensions[configuration_file, resource, metric_category/metric_name, dimension] | Discover dimensions from Azure's resources | {#DIMENSION} |
azure.discover.dimensions.namespace[configuration_file, resource, metric_category/metric_name, dimension, metric namespace] | Discover dimensions from Azure's resources using metric namespace | {#DIMENSION} |

Some examples of namespaces are:

azure.applicationinsights
insights.container/containers
insights.container/nodes
insights.container/pods
insights.container/persistentvolumes

* Read more about metric namespaces here: https://aka.ms/metricnamespaces



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

* The first parameter should be the path to the configuration file.
* Application Insights queries need application ID as second parameter or a matching key to locate an ID from the configuration file. This can be obtained from "Azure Portal > Application Insights > API Access".
* Log Analytics queries need workspace ID as second parameter or a matching key to locate an ID from the configuration file. This can be obtained from "Azure Portal > Log Analytics workspace > Overview".
* The last parameter can either be a matching key to locate the query from the configuration file or the Kusto query itself.


### Azure Logic App queries

Item Syntax | Description | Response |
----------- | ----------- | -------- |
azure.logic.apps[configuration_file, resource_group] | Discover Azure Logic App workflows | {#WORKFLOW_ID}, {#WORKFLOW_NAME}
azure.logic.apps[configuration_file, resource_group, workflow_name] | Discover Azure Logic App workflow triggers | {#TRIGGER_ID}, {#TRIGGER_NAME}
azure.logic.apps[configuration_file, resource_group, workflow_name, trigger_name ] | Discover Azure Logic App workflow trigger history | {#HISTORY_ID}, {#HISTORY_NAME}, {#HISTORY_STATUS}


---


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


### CLI example, list available resources from Azure's services
```
azure_discover_resources <path_to_config_file>
```


### CLI example, list available metrics from resource
```
azure_discover_metrics <path_to_config_file> <resource>
```


### CLI example, list available dimensions from resource
```
azure_discover_dimensions <path_to_config_file> <resource> <metric> <dimension>
azure_discover_dimensions <path_to_config_file> <resource> <metric> <dimension> --metric-namespace <metric_namespace>
```


### CLI example, list available roleInstances and roleNames from resource
```
azure_discover_roles <path_to_config_file> <resource> <metric> <dimension>
```


### CLI example, retrieve metric from resource
```
azure_metric <path_to_config_file> <resource> <metric> <statistic> <timegrain> --timeshift <timeshift>
```


### Possible values for statistic-argument

Average, Count, Minimum, Maximum, Total



### Possible values for timegrain-argument

Value | Description  |
----- | ------------ |
PT1M  | One minute   |
PT5N  | Five minutes |
PT1H  | One hour     |
PT3H  | Three hours  |
P1D   | One day      |



### Timeshift-argument

Timeshift argument expects the number of minutes to delay the query. In some cases the data is not
available instantly so it's advisable to delay the data retrieval. A good starting point is to
delay all metric queries for 5 minutes.



### CLI example, Kusto queries
```
azure_query application_insights <path_to_config_file> <application_ID_or_matching_key> <kusto_query_or_matching_key>
azure_query log_analytics <path_to_config_file> <workspace_ID_or_matching_key> <kusto_query_or_matching_key>
```
