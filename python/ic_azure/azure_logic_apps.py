#!/usr/bin/python3

# Python imports
import json
from argparse import ArgumentParser

# Azure client imports
from ic_azure.azure_client import AzureClient


def main(args=None):
    parser = ArgumentParser(
        description="Discover workflows from Azure Logic Apps."
    )

    parser.add_argument("config", type=str, help="Path to configuration file")
    parser.add_argument("resource_group", type=str,
                        help="Resource group name.")
    parser.add_argument("-t", "--trigger", dest="trigger", type=str,
                        help="Logic App trigger name.")
    parser.add_argument("-w", "--workflow", dest="workflow", type=str,
                        help="Logic App workflow name.")
    parser.add_argument("--version", dest="version", default="2016-06-01",
                        type=str, help="Azure REST API version.")

    args = parser.parse_args(args)

    # Instantiate Azure client
    azure_client = AzureClient(args)

    # Generate query base URL
    url = "https://management.azure.com"
    url += "/subscriptions/{}".format(azure_client.subscription_id)
    url += "/resourceGroups/{}".format(args.resource_group)
    url += "/providers/Microsoft.Logic"

    # Modify query based on arguments
    if args.trigger:  # Trigger history
        url += "/workflows/{}".format(args.workflow)
        url += "/triggers/{}".format(args.trigger)
        url += "/histories?api-version={}".format(args.version)
    elif args.workflow:  # Triggers
        url += "/workflows/{}".format(args.workflow)
        url += "/triggers?api-version={}".format(args.version)
    else:  # Workflows
        url += "/workflows?api-version={}".format(args.version)

    # Run query to API
    response = azure_client.query(method="GET", url=url)

    # Print results depending on arguments
    discovery = []
    for item in response.get("value"):
        if args.trigger:  # Trigger history
            discovery.append({
                "{#HISTORY_ID}": item.get("id"),
                "{#HISTORY_STATUS}": item.get("properties").get("status"),
                "{#HISTORY_NAME}": item.get("name")
            })
            continue

        # Only include enabled items of triggers and workflows
        if item.get("properties").get("state") != "Enabled":
            continue

        if args.workflow:  # Triggers
            discovery.append({
                "{#TRIGGER_ID}": item.get("id"),
                "{#TRIGGER_NAME}": item.get("name")
            })
        else:  # Workflows
            discovery.append({
                "{#WORKFLOW_ID}": item.get("id"),
                "{#WORKFLOW_NAME}": item.get("name")
            })

    # Output discovery
    discovery = {"data": discovery}
    print(json.dumps(discovery))


if __name__ == "__main__":
    main()
