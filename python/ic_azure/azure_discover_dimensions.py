#!/usr/bin/env python

# Python imports
from datetime import datetime, timedelta
from argparse import ArgumentParser
import json

# Azure client imports
from ic_azure.azure_client import AzureClient


class AzureDiscoverRoles(object):
    """Retrieve roles from Azure's resource"""

    def __init__(self, azure_client):
        self._client = azure_client.client()
        self.subscription_id = azure_client.subscription_id
        self.resources = azure_client.resources

    # Method to retrieve roles from Azure's resource
    def get_roles(self, resource, metric, dimension, metric_namespace):

        # Declare variables
        rolesList = []

        # Calculate start/end times
        end_time = datetime.utcnow() - timedelta(minutes=5)
        start_time = end_time - timedelta(days=1)

        # Read resource from config using key
        if not resource.startswith("/subscriptions"):
            resource = self.resources.get(resource)

        # Retrieve instance data
        metrics_data = self._client.metrics.list(
            resource,
            timespan="{}/{}".format(
                start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            ),
            interval="P1D",
            metricnames=metric,
            aggregation="Total",
            result_type="Metadata",
            filter=dimension + " eq '*'",
            metricnamespace=metric_namespace
        )

        # Loop through metric data and retrieve instances
        for item in metrics_data.value:
            for timeserie in item.timeseries:
                for data in timeserie.metadatavalues:

                    # Don't add duplicates into roles list
                    if data.__dict__.get("value") in rolesList:
                        continue

                    rolesList.append(data.__dict__.get("value"))

        return rolesList


def main(args=None):
    parser = ArgumentParser(
        description="Retrieve roles from Azure's resource"
    )

    parser.add_argument("config", type=str, help="Path to configuration file")
    parser.add_argument("resource", type=str, help="Azure resource to use")
    parser.add_argument("metric", type=str, help="Metric to obtain")
    parser.add_argument("dimension", type=str, help="Dimension to use")
    parser.add_argument("-m", "--metric-namespace", default=None, type=str,
                        dest="metric_namespace",
                        help="Metric namespace for Azure resource query.")

    args = parser.parse_args(args)

    # Instantiate Azure client
    azure_client = AzureClient(args)

    # Instantiate role discovery
    client = AzureDiscoverRoles(azure_client)

    # Find roles using discovery
    rolesList = client.get_roles(
        args.resource,
        args.metric,
        args.dimension,
        args.metric_namespace
    )

    # Create dictionary from role data
    names = []
    for item in rolesList:
        names.append({"{#DIMENSION}": item, "{#ROLE_NAME}": item})

    # Output roles
    discovery = {"data": names}
    print(json.dumps(discovery))


if __name__ == "__main__":
    main()
