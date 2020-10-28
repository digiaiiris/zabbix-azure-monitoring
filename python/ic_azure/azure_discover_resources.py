#!/usr/bin/python3

# Python imports
import json
from argparse import ArgumentParser

# Azure client imports
from azure_client import AzureClient


class AzureDiscoverResources(object):
    """Discover resources from Azure's services."""

    def __init__(self, azure_client):
        self._client = azure_client.resource_client()

    def find_resources(self):
        resourceList = []

        # List resources using client
        for resource in self._client.resources.list():
            resourceList.append(resource.id)

        return resourceList


def main(args=None):
    parser = ArgumentParser(
        description="Discover resources from Azure's services"
    )

    parser.add_argument("config", type=str, help="Path to configuration file")

    args = parser.parse_args(args)

    # Instantiate Azure resource client
    azure_resource_client = AzureClient(args)

    # Instantiate resource discovery
    resource_client = AzureDiscoverResources(azure_resource_client)

    # Find resources using discovery
    resourceList = resource_client.find_resources()

    # Create dictionary from resource data
    names = []
    for item in resourceList:
        names.append({
            "{#RESOURCE}": item,
            "{#RESOURCE_GROUP}": item.split("/")[4],
            "{#RESOURCE_TYPE}": item.split("/")[6] + "/" + item.split("/")[7],
            "{#RESOURCE_NAME}": item.split("/")[8]
        })

    # Output resources
    discovery = {"data": names}
    print(json.dumps(discovery))


if __name__ == "__main__":
    main()
