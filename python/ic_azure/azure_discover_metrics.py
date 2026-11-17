#!/usr/bin/env python

# Python imports
import json
from argparse import ArgumentParser

# Must be imported before the Azure SDK to measure import time
from ic_azure import azure_logging

# Azure client imports
from ic_azure.azure_client import AzureClient


class AzureDiscoverMetrics(object):
    """Discover metrics from Azure's resources."""

    def __init__(self, azure_client):
        self._client = azure_client.client()
        self.subscription_id = azure_client.subscription_id
        self.resources = azure_client.resources

    def find_services(self, resource, metric_namespace):
        servicesList = []

        # Read resource from config using key
        if not resource.startswith("/subscriptions"):
            resource = self.resources.get(resource)
        azure_logging.set_resource(resource)

        # List metrics from resource
        for metric in self._client.metric_definitions.list(
            resource,
            metricnamespace=metric_namespace
        ):
            servicesList.append(metric.name.value)

        return servicesList


@azure_logging.log_run("azure_discover_metrics")
def main(args=None):
    parser = ArgumentParser(
        description="Discover metrics from Azure's resources."
    )

    parser.add_argument("config", type=str, help="Path to configuration file")
    parser.add_argument("resource", type=str, help="Azure resource to use")
    parser.add_argument("-m", "--metric-namespace", default=None, type=str,
                        dest="metric_namespace",
                        help="Metric namespace for Azure resource query.")

    args = parser.parse_args(args)
    azure_logging.set_context(resource=args.resource, namespace=args.metric_namespace)

    # Instantiate Azure client
    azure_client = AzureClient(args)

    # Instantiate metric discovery
    client = AzureDiscoverMetrics(azure_client)

    # Find metric services using discovery
    servicesList = client.find_services(
        args.resource,
        args.metric_namespace
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
    azure_logging.emit(json.dumps(discovery), items=len(names))


if __name__ == "__main__":
    main()
