#!/usr/bin/python

# Python imports
import json
from argparse import ArgumentParser

# Azure client imports
from azure_client import AzureClient


class InsightsDiscovery(object):
    """Discover available metrics from Azure's Insights components."""

    def __init__(self, azure_client):
        self._client = azure_client.client()
        self.subscription_id = azure_client.subscription_id

    def find_services(self, resource_group, resource_name):
        servicesList = []

        # Create resource ID
        resource_id = "subscriptions/{}/resourceGroups/{}".format(
            self.subscription_id,
            resource_group
        )
        resource_id += "/providers/microsoft.insights/components/{}".format(
            resource_name
        )

        # List metrics from resource
        for metric in self._client.metric_definitions.list(resource_id):
            servicesList.append(metric.name.value)

        return servicesList


def main(args=None):
    parser = ArgumentParser(description="Discover Microsoft Insights services")

    parser.add_argument("-c", "--config", help="Path to configuration file.")
    parser.add_argument("-g", "--resource-group", dest="resource_group",
                        help="Insights resource group")
    parser.add_argument("-r", "--resource-name", dest="resource_name",
                        help="Insights resource name")

    args = parser.parse_args(args)

    # Instantiate Azure client
    azure_client = AzureClient(args)

    # Instantiate Insights discovery
    client = InsightsDiscovery(azure_client)

    # Find metric services using discovery
    servicesList = client.find_services(
        args.resource_group,
        args.resource_name
    )

    # Create dictionary from metrics data
    names = []
    for item in servicesList:
        names.append({
            "{#METRIC_CATEGORY}": item.split("/")[0],
            "{#METRIC_NAME}": item.split("/")[-1]
        })

    # Output metric services
    discovery = {"data": names}
    print json.dumps(discovery)


if __name__ == "__main__":
    main()
