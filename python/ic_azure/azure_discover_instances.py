#!/usr/bin/python

# Python imports
from datetime import datetime, timedelta
from argparse import ArgumentParser
import json
import re

# Azure client imports
from azure_client import AzureClient


class AzureDiscoverInstances(object):
    """Retrieve instances from Azure's resource"""

    def __init__(self, azure_client):
        self._client = azure_client.client()
        self.subscription_id = azure_client.subscription_id

    # Method to retrieve instances from Azure's resource
    def get_instances(self, resource_group, provider_name, resource_type,
                      resource_name, metric):

        # Declare variables
        instanceList = []

        # Calculate start/end times
        end_time = datetime.utcnow() - timedelta(minutes=5)
        start_time = end_time - timedelta(minutes=1)

        # Create resource ID
        resource_id = "subscriptions/{}/resourceGroups/{}".format(
            self.subscription_id,
            resource_group
        )
        resource_id += "/providers/{}/{}/{}".format(
            provider_name,
            resource_type,
            resource_name
        )

        # Retrieve instance data
        metrics_data = self._client.metrics.list(
            resource_id,
            timespan="{}/{}".format(
                start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            ),
            interval="PT1M",
            metricnames=metric,
            aggregation="Total",
            filter="cloud/roleInstance eq '*'"
        )

        # Loop through metric data and retrieve instances
        for item in metrics_data.value:
            for timeserie in item.timeseries:
                for data in timeserie.metadatavalues:
                    instanceList.append(data.__dict__.get("value"))

        return instanceList


def main(args=None):
    parser = ArgumentParser(
        description="Retrieve instances from Azure's resource"
    )

    parser.add_argument("-c", "--config", help="Path to configuration file.")
    parser.add_argument("-g", "--resource-group", dest="resource_group",
                        help="ResourceGroup for resource.")
    parser.add_argument("-p", "--provider-name", dest="provider_name",
                        help="Company.ProviderName for resource.")
    parser.add_argument("-t", "--resource-type", dest="resource_type",
                        help="ResourceType for resource.")
    parser.add_argument("-r", "--resource-name", dest="resource_name",
                        help="ResourceName for resource.")
    parser.add_argument("metric", help="Metric to obtain")

    args = parser.parse_args(args)

    # Instantiate Azure client
    azure_client = AzureClient(args)

    # Instantiate instance discovery
    client = AzureDiscoverInstances(azure_client)

    # Find instances using discovery
    instanceList = client.get_instances(
        args.resource_group,
        args.provider_name,
        args.resource_type,
        args.resource_name,
        args.metric
    )

    # Create dictionary from instance data
    names = []
    for item in instanceList:
        names.append({"{#INSTANCE_NAME}": item})

    # Output instances
    discovery = {"data": names}
    print json.dumps(discovery)


if __name__ == "__main__":
    main()
