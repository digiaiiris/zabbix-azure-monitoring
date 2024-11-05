#!/usr/bin/env python

# Python imports
from datetime import datetime, timedelta
from argparse import ArgumentParser
import json
import sys

# Azure client imports
from ic_azure.azure_client import AzureClient

class AzureDiscoverDimensions(object):
    """Retrieve dimensions from Azure's resource"""

    def __init__(self, azure_client):
        self._client = azure_client.client()
        self.subscription_id = azure_client.subscription_id
        self.resources = azure_client.resources

    def get_data(self, resource, metric, queryfilter, metric_namespace):

        # Calculate start/end times
        end_time = datetime.now() - timedelta(minutes=5)
        start_time = end_time - timedelta(hours=1)

        try:
            # Retrieve instance data
            metrics_data = self._client.metrics.list(
                resource,
                timespan="{}/{}".format(
                    start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
                ),
                interval="PT1H",
                metricnames=metric,
                aggregation="Total",
                result_type="Metadata",
                filter=queryfilter,
                metricnamespace=metric_namespace
            )
        except Exception as error:
            sys.exit(f"Client request failed. {error}")

        return metrics_data

    # Method to retrieve dimensions from Azure's resource
    def get_dimensions(self, resource, metric, dimension, extent, metric_namespace):

        # Declare variables
        dimensionsList = []

        # Read resource from config using key
        if not resource.startswith("/subscriptions"):
            resource = self.resources.get(resource)
        
        filter = dimension + " eq '*'"
        result = self.get_data(resource, metric, filter, metric_namespace)

        # Loop through metric data and retrieve instances
        for item in result.value:
            for timeserie in item.timeseries:
                for data in timeserie.metadatavalues:
                    # Don't add duplicates into dimensions list
                    name = data.__dict__.get("value")
                    if name in dimensionsList:
                        continue
                    
                    dimensionsList.append({"{#DIMENSION}": name, "{#ROLE_NAME}": name})
                    
                    # Get second dimensions (extents) for the discovered resource
                    if extent:
                        extent_filter = f"{dimension} eq '{name}' and {extent} eq '*'"
                        extent_data = self.get_data(resource, metric, extent_filter, metric_namespace)
                        
                        # Loop through metric data and retrieve instances
                        for property in extent_data.value:
                            for serie in property.timeseries:
                                for info in serie.metadatavalues:
                                    # Don't add duplicates into dimensions list
                                    name2 = info.__dict__.get("value")
                                    if name2 in dimensionsList:
                                        continue
                    
                                    dimensionsList.append({"{#DIMENSION}": name, "{#ROLE_NAME}": name, "{#EXTENT}": name2})
                        
                        # Remove objects without extent information
                        dimensionsList = [element for element in dimensionsList if "{#EXTENT}" in element]

        return dimensionsList

def main(args=None):
    parser = ArgumentParser(
        description="Retrieve dimensions from Azure's resource"
    )

    parser.add_argument("config", type=str, help="Path to configuration file")
    parser.add_argument("resource", type=str, help="Azure resource to use")
    parser.add_argument("metric", type=str, help="Metric to obtain")
    parser.add_argument("dimension", type=str, help="Primary dimension to use, i.e. node")
    parser.add_argument("--extent", default=None, type=str, help="Second dimension (extent) to use, i.e. device")
    parser.add_argument("-m", "--metric-namespace", default=None, type=str,
                        dest="metric_namespace",
                        help="Metric namespace for Azure resource query.")

    args = parser.parse_args(args)

    # Instantiate Azure client
    azure_client = AzureClient(args)

    # Instantiate role discovery
    client = AzureDiscoverDimensions(azure_client)

    # Find dimensions using discovery
    dimension_data= client.get_dimensions(
        args.resource,
        args.metric,
        args.dimension,
        args.extent,
        args.metric_namespace
    )

    # Output dimensions
    discovery = {"data": dimension_data}
    print(json.dumps(discovery))


if __name__ == "__main__":
    main()