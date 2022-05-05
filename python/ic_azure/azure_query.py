#!/usr/bin/python3

# Python imports
import json
from argparse import ArgumentParser

# Azure client imports
from ic_azure.azure_client import AzureClient

# Declare variables
application_id = None
endpoints = {
    "application_insights": "https://api.applicationinsights.io/",
    "log_analytics": "https://api.loganalytics.io/"
}
query = None
url = None
workspace_id = None


def main(args=None):
    parser = ArgumentParser(
        description="Run Kusto queries to Azure's REST APIs"
    )

    parser.add_argument("endpoint", choices=[k for k in endpoints], type=str,
                        help="API to query for, application_insights or " +
                        "log_analytics.")
    parser.add_argument("config", type=str, help="Path to configuration file.")
    parser.add_argument("id", type=str, help="Application ID for Kusto " +
                        "queries. Workspace ID for Log Analytics queries. " +
                        "Key to match predefined IDs.")
    parser.add_argument("query", type=str, help="Query to run or key to " +
                        "match predefined query.")

    args = parser.parse_args(args)

    # Instantiate Azure Kusto-client
    azure_client = AzureClient(args, api=endpoints[args.endpoint], queries=True)

    # Match predefined queries
    query = args.query
    if azure_client.queries.get(query):
        query = azure_client.queries.get(query)

    # Match predefined application IDs and generate query URL
    if args.endpoint == "application_insights":
        application_id = args.id

        # Retrieve application ID using key
        if azure_client.application_ids.get(application_id):
            application_id = azure_client.application_ids.get(application_id)

        # Set query URL
        url = "{}v1/apps/{}/query".format(
            endpoints[args.endpoint],
            application_id
        )

    # Match predefined workspace IDs and generate query URL
    elif args.endpoint == "log_analytics":
        workspace_id = args.id

        # Retrieve workspace ID using key
        if azure_client.workspace_ids.get(workspace_id):
            workspace_id = azure_client.workspace_ids.get(workspace_id)

        # Set query URL
        url = "{}v1/workspaces/{}/query".format(
            endpoints[args.endpoint],
            workspace_id
        )

    # Execute query
    response = azure_client.query(
        method="POST",
        json={"query": query},
        url=url
    )

    # Print response
    print(json.dumps(response))


if __name__ == "__main__":
    main()
