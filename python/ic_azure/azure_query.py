#!/usr/bin/python3

# Python imports
import json
from argparse import ArgumentParser

# Azure client imports
from azure_client import AzureClient


def main(args=None):
    parser = ArgumentParser(
        description="Run Kusto queries to Azure's REST APIs"
    )

    parser.add_argument("type", choices=["kusto", "log_analytics"], type=str,
                        help="Type of query, kusto or log_analytics.")
    parser.add_argument("config", type=str, help="Path to configuration file.")
    parser.add_argument("id", type=str, help="Application ID for Kusto " +
                        "queries. Workspace ID for Log Analytics queries. " +
                        "Key to match predefined IDs.")
    parser.add_argument("query", type=str, help="Query to run or key to " +
                        "match predefined query.")

    args = parser.parse_args(args)

    # Azure REST API URL
    if args.type == "kusto":
        api = "https://api.applicationinsights.io/"
    elif args.type == "log_analytics":
        api = "https://api.loganalytics.io/"
    else:
        raise ValueError("Invalid type argument. Use kusto or log_analytics.")

    # Instantiate Azure Kusto-client
    azure_client = AzureClient(args, api=api, queries=args.type)

    # Match predefined queries
    query = args.query
    if azure_client.queries.get(query):
        query = azure_client.queries.get(query)

    # Match predefined application IDs and generate query URL
    if args.type == "kusto":
        application_id = args.id

        # Retrieve application ID using key
        if azure_client.application_ids.get(application_id):
            application_id = azure_client.application_ids.get(application_id)

        # Set query URL
        url = "{}v1/apps/{}/query".format(api, application_id)

    # Match predefined workspace IDs and generate query URL
    elif args.type == "log_analytics":
        workspace_id = args.id

        # Retrieve application ID using key
        if azure_client.workspace_ids.get(workspace_id):
            workspace_id = azure_client.workspace_ids.get(workspace_id)

        # Set query URL
        url = "{}v1/workspaces/{}/query".format(api, workspace_id)

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
