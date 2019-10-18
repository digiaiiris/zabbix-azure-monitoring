#!/usr/bin/python

# Python imports
from datetime import datetime, timedelta
from argparse import ArgumentParser
import json
import re

# Azure client imports
from azure_client import AzureClient


class AzureDiscoverRoles(object):
    """Retrieve roles from Azure's resource"""

    def __init__(self, azure_client):
        self._client = azure_client.client()
        self.subscription_id = azure_client.subscription_id

    # Method to retrieve roles from Azure's resource
    def get_roles(self, resource_group, provider_name, resource_type,
                  resource_name, metric, dimension):

        # Declare variables
        rolesList = []

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
            result_type="Metadata",
            filter=dimension + " eq '*'"
        )

        # Loop through metric data and retrieve instances
        for item in metrics_data.value:
            for timeserie in item.timeseries:
                for data in timeserie.metadatavalues:
                    rolesList.append(data.__dict__.get("value"))

        return rolesList


def main(args=None):
    parser = ArgumentParser(
        description="Retrieve roles from Azure's resource"
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
    parser.add_argument("dimension", help="Dimension to use")

    args = parser.parse_args(args)

    # Instantiate Azure client
    azure_client = AzureClient(args)

    # Instantiate role discovery
    client = AzureDiscoverRoles(azure_client)

    # Find roles using discovery
    rolesList = client.get_roles(
        args.resource_group,
        args.provider_name,
        args.resource_type,
        args.resource_name,
        args.metric,
        args.dimension
    )

    # Create dictionary from role data
    names = []
    for item in rolesList:
        names.append({"{#ROLE_NAME}": item})

    # Output roles
    discovery = {"data": names}
    print(json.dumps(discovery))


if __name__ == "__main__":
    main()
