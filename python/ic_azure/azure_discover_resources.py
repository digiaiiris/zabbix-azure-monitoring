#!/usr/bin/env python

# Python imports
import json
import os
import re
from argparse import ArgumentParser

# Azure client imports
from ic_azure.azure_client import AzureClient


class AzureDiscoverResources(object):
    """Discover resources from Azure's services."""

    def __init__(self, azure_client):
        self._client = azure_client.resource_client()

    def find_resources(self):

        # Declare variables
        resources = []

        # List resources and tags using client
        for resource in self._client.resources.list():

            type_match = re.search('providers(\/[^\/]+){1,4}', resource.id).group(0)

            # Apply resource data
            resource_data = {
            "{#RESOURCE}": resource.id,
            "{#RESOURCE_GROUP}": re.search('resourceGroups\/([^\/]*)', resource.id).group(1),
            "{#RESOURCE_TYPE}": re.sub('providers\/([^\/]+\/[^\/]+)\/[^\/]+(\/[^\/]*)?',r'\1\2', type_match),
            "{#RESOURCE_NAME}": re.search('([^\/]*)$', resource.id).group(1)
            }

            # Additionally return possible tags
            if resource.tags:
                for tag in resource.tags:
                    resource_data["{#TAG_" + tag.upper() + "}"] = resource.tags[tag]

            # Set resource data into resources list
            resources.append(resource_data)

        return resources


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
    resources = resource_client.find_resources()

    # Output resources
    print(json.dumps({"data": resources}))


if __name__ == "__main__":
    main()
