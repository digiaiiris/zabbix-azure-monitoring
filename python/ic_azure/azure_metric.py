#!/usr/bin/python3

# Python imports
from datetime import datetime, timedelta
from argparse import ArgumentParser
import re
import sys

# Azure imports
from msrest.exceptions import AuthenticationError, ClientRequestError, \
    DeserializationError, HttpOperationError, SerializationError, \
    TokenExpiredError, ValidationError

# Azure client imports
from ic_azure.azure_client import AzureClient


class AzureMetric(object):
    """Retrieve metrics from Azure's resources"""

    def __init__(self, azure_client):
        self._client = azure_client.client()
        self.subscription_id = azure_client.subscription_id
        self.resources = azure_client.resources
        self.timeout = azure_client.timeout

    # Method to retrieve metrics from Azure's resources
    def get_metric(self, resource, metric, statistic, timegrain, timeshift,
                   instance_name, role_name):

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

        # Set instance/role name to filter
        if instance_name:
            filter = "cloud/roleInstance eq '{}'".format(instance_name)
        elif role_name:
            filter = "cloud/roleName eq '{}'".format(role_name)

        # Read resource from config using key
        if not resource.startswith("/subscriptions"):
            resource = self.resources.get(resource)

        # Retrieve metric data
        try:
            metrics_data = self._client.metrics.list(
                resource,
                timespan="{}/{}".format(
                    start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
                ),
                interval=timegrain,
                metricnames=metric,
                aggregation=statistic,
                result_type="Data",
                filter=filter,
                timeout=self.timeout
            )
        except AuthenticationError as e:
            print("Client request failed to authenticate. {}".format(e))
            sys.exit(1)
        except ClientRequestError as e:
            print("Client request failed. {}".format(e))
            sys.exit(1)
        except DeserializationError as e:
            print("Error raised during response deserialization. {}".format(e))
            sys.exit(1)
        except HttpOperationError as e:
            print("HTTP operation error. {}".format(e))
            sys.exit(1)
        except SerializationError as e:
            print("Error raised during request serialization. {}".format(e))
            sys.exit(1)
        except TokenExpiredError as e:
            print("OAuth token expired. {}".format(e))
            sys.exit(1)
        except ValidationError as e:
            print("Request parameter validation failed. {}".format(e))
            sys.exit(1)
        except Exception as e:
            print("An exception occured. {}".format(e))
            sys.exit(1)

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

    parser.add_argument("config", type=str, help="Path to configuration file.")
    parser.add_argument("resource", type=str, help="Azure resource to use.")
    parser.add_argument("metric", type=str, help="Metric to obtain.")
    parser.add_argument("statistic", type=str, help="Statistic to retrieve, " +
                        "e.g. Average, Count, Minimum, Maximum, Total.")
    parser.add_argument("timegrain", type=str, help="Timegrain for metric, " +
                        "e.g. PT1M, PT1H, P1D.")
    parser.add_argument("-i", "--instance-name", type=str,
                        dest="instance_name",
                        help="InstanceName for resource.")
    parser.add_argument("-r", "--role-name", type=str, dest="role_name",
                        help="RoleName for resource.")
    parser.add_argument("--timeshift", default=0, type=int,
                        help="Time shift for interval.")

    args = parser.parse_args(args)

    # Instantiate Azure client
    azure_client = AzureClient(args)

    # Instantiate Azure metrics
    client = AzureMetric(azure_client)

    value = client.get_metric(
        args.resource,
        args.metric,
        args.statistic,
        args.timegrain,
        args.timeshift,
        args.instance_name,
        args.role_name
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
