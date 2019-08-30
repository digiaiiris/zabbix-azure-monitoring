#!/usr/bin/python

# Python imports
from datetime import datetime, timedelta
from argparse import ArgumentParser
import re

# Azure client imports
from azure_client import AzureClient


class AzureMetric(object):
    """Retrieve metrics from Azure's resources"""

    def __init__(self, azure_client):
        self._client = azure_client.client()
        self.subscription_id = azure_client.subscription_id

    # Method to retrieve metrics from Azure's resources
    def get_metric(self, resource_group, provider_name, resource_type,
                   resource_name, instance_name, role_name, metric, statistic,
                   timegrain, timeshift):

        # Declare variables
        filter = None
        interval = -1
        ret_val = ""

        # Retrieve interval and timeunit
        result = re.search(r"^PT?([\d]+)([DHM])$", timegrain)

        # Check the result object
        if not result:
            raise ValueError("Timegrain value is invalid.")

        # Retrieve and check interval
        interval = int(result.group(1))
        if interval < 1:
            raise ValueError("Timegrain interval is not valid.")

        # Calculate end time
        end_time = datetime.utcnow() - timedelta(seconds=timeshift)

        # Retrieve time unit and calculate start time
        if result.group(2) == "D":
            start_time = end_time - timedelta(days=interval)
        elif result.group(2) == "H":
            start_time = end_time - timedelta(hours=interval)
        elif result.group(2) == "M":
            start_time = end_time - timedelta(minutes=interval)
        else:
            raise ValueError("Unable to retrieve unit from timegrain.")

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

        # Set instance/role name to filter
        if instance_name:
            filter = "cloud/roleInstance eq '{}'".format(instance_name)
        elif role_name:
            filter = "cloud/roleName eq '{}'".format(role_name)

        # Retrieve metric data
        metrics_data = self._client.metrics.list(
            resource_id,
            timespan="{}/{}".format(
                start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            ),
            interval=timegrain,
            metricnames=metric,
            aggregation=statistic,
            result_type="Data",
            filter=filter
        )

        # Loop through metric data and retrieve relevant value
        for item in metrics_data.value:
            for timeserie in item.timeseries:
                for data in timeserie.data:
                    ret_val = data.__dict__.get(statistic.lower())

        return ret_val


def main(args=None):
    parser = ArgumentParser(
        description="Retrieve metrics from Azure's resources"
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
    parser.add_argument("-i", "--instance-name", dest="instance_name",
                        help="InstanceName for resource.")
    parser.add_argument("-n", "--role-name", dest="role_name",
                        help="RoleName for resource.")
    parser.add_argument("--timeshift", type=int, default=300,
                        help="Time shift for interval")
    parser.add_argument("metric", help="Metric to obtain")
    parser.add_argument("statistic", help="Statistic to retrieve. e.g. " +
                        "Average, Count, Minimum, Maximum, Total")
    parser.add_argument("timegrain", help="Timegrain for metric. e.g. " +
                        "PT1M, PT1H, P1D")

    args = parser.parse_args(args)

    # Instantiate Azure client
    azure_client = AzureClient(args)

    # Instantiate Azure metrics
    client = AzureMetric(azure_client)

    value = client.get_metric(
        args.resource_group,
        args.provider_name,
        args.resource_type,
        args.resource_name,
        args.instance_name,
        args.role_name,
        args.metric,
        args.statistic,
        args.timegrain,
        args.timeshift
    )

    # If value is empty or we didn't get a value, print zero. Otherwise print
    # the retrieved value.
    if not value:
        print(0)
    elif value == "":
        print(0)
    else:
        print(value)


if __name__ == "__main__":
    main()
