#!/usr/bin/env python

# Python imports
import json
from argparse import ArgumentParser

# Must be imported before the Azure SDK to measure import time
from ic_azure import azure_logging

# Azure client imports
from ic_azure.azure_client import AzureClient


@azure_logging.log_run("azure_discover_webapp_instances")
def main(args=None):
    """Discover Web App scale-out instances.
    Uses the following REST API:
    https://learn.microsoft.com/en-us/rest/api/appservice/web-apps/list-instance-identifiers?view=rest-appservice-2022-03-01  # noqa
    """

    parser = ArgumentParser(
        description="Discover WebApp scale-out instances"
    )

    parser.add_argument("config", type=str, help="Path to configuration file")
    parser.add_argument("resource_group", type=str,
                        help="Resource group name.")
    parser.add_argument("webapp", type=str, help="Web App name")
    args = parser.parse_args(args)
    azure_logging.set_context(rg=args.resource_group, webapp=args.webapp)

    # Instantiate Azure client
    azure_client = AzureClient(args)

    # Generate query base URL
    url = "https://management.azure.com"
    url += "/subscriptions/{}".format(azure_client.subscription_id)
    url += "/resourceGroups/{}".format(args.resource_group)
    url += "/providers/Microsoft.Web/sites"
    url += "/{}".format(args.webapp)
    url += "/instances?api-version=2022-03-01"

    # Run query to API
    response = azure_client.query(method="GET", url=url)

    # Print results depending on arguments
    discovery = []
    for item in response.get("value"):
        props = item.get("properties")
        discovery.append({
            "{#MACHINE_NAME}": props.get("machineName"),
            "{#STATE}": props.get("state"),
            "{#STATUS_URL}": props.get("statusUrl"),
            "{#HEALTHCHECK_URL}": props.get("healthCheckUrl")
        })

    # Output discovery
    azure_logging.emit(json.dumps({"data": discovery}), items=len(discovery))


if __name__ == "__main__":
    main()
