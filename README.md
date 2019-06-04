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
