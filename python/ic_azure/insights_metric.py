#!/usr/bin/python

# Python imports
from datetime import datetime, timedelta
from argparse import ArgumentParser

# Azure client imports
from azure_client import AzureClient


class InsightsMetric(object):
    """Retrieve metric data from Azure's Microsoft Insights components."""

    def __init__(self, azure_client):
        self._client = azure_client.client()
        self.subscription_id = azure_client.subscription_id

    # Method to retrieve metrics from Microsoft Insight resources
    def get_metric(self, resource_group, resource_name, interval, metric,
                   statistic, timeshift):

        # Declare variables
        ret_val = -1

        # Calculate timestamps
        end_time = datetime.utcnow() - timedelta(seconds=timeshift)
        start_time = end_time - timedelta(seconds=interval)

        # Create resource ID
        resource_id = "subscriptions/{}/resourceGroups/{}".format(
            self.subscription_id,
            resource_group
        )
        resource_id += "/providers/microsoft.insights/components/{}".format(
            resource_name
        )

        # Get timegrain based on interval
        # Possible values: None, PT1M, PT1H, P1D
        quotient, remainder = divmod(interval, 60)
        if quotient <= 1:
            timegrain = 'PT1M'
        elif quotient <= 60:
            timegrain = 'PT1H'
        else:
            timegrain = 'P1D'

        # Retrieve metric data
        metrics_data = self._client.metrics.list(
            resource_id,
            timespan="{}/{}".format(
                start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            ),
            interval=timegrain,
            metricnames=metric,
            aggregation=statistic
        )

        # Loop through metric data and retrieve relevant value
        for item in metrics_data.value:
            for timeserie in item.timeseries:
                for data in timeserie.data:
                    ret_val = data.total

        return ret_val


def main(args=None):
    parser = ArgumentParser(description="Retrieve Azure Insights metrics")

    parser.add_argument("-c", "--config", help="Path to configuration file.")
    parser.add_argument("-g", "--resource-group", dest="resource_group",
                        help="Insights resource group")
    parser.add_argument("-r", "--resource-name", dest="resource_name",
                        help="Insights resource name")
    parser.add_argument("--timeshift", type=int, default=0,
                        help="Time shift for interval")
    parser.add_argument("metric", help="Metric to obtain")
    parser.add_argument("interval", type=int, help="Statistic interval")
    parser.add_argument("statistic", help="Statistic to retrieve. e.g. " +
                        "None, Average, Count, Minimum, Maximum, Total")

    args = parser.parse_args(args)

    # Instantiate Azure client
    azure_client = AzureClient(args)

    # Instantiate Insights metrics
    client = InsightsMetric(azure_client)

    value = client.get_metric(
        args.resource_group,
        args.resource_name,
        args.interval,
        args.metric,
        args.statistic,
        args.timeshift
    )

    # Do not print value if it is below zero
    if value == -1:
        print("")
    else:
        print(value)


if __name__ == "__main__":
    main()
