#!/usr/bin/python

# Python imports
import json
from argparse import ArgumentParser

# Azure client imports
from azure_client import AzureClient


class AzureDiscoverMetrics(object):
    """Discover metrics from Azure's resources."""

    def __init__(self, azure_client):
        self._client = azure_client.client()
        self.subscription_id = azure_client.subscription_id
        self.resources = azure_client.resources

    def find_services(self, resource):
        servicesList = []

        # Read resource from config using key
        if not resource.startswith("/subscriptions"):
            resource = self.resources.get(resource)

        # List metrics from resource
        for metric in self._client.metric_definitions.list(resource):
            servicesList.append(metric.name.value)

        return servicesList


def main(args=None):
    parser = ArgumentParser(
        description="Discover metrics from Azure's resources."
    )


    parser.add_argument("config", type=str, help="Path to configuration file")
    parser.add_argument("resource", type=str, help="Azure resource to use")

    args = parser.parse_args(args)

    # Instantiate Azure client
    azure_client = AzureClient(args)

    # Instantiate metric discovery
    client = AzureDiscoverMetrics(azure_client)

    # Find metric services using discovery
    servicesList = client.find_services(
        args.resource
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
    print(json.dumps(discovery))


if __name__ == "__main__":
    main()
