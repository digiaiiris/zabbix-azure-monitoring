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

    parser.add_argument("config", type=str, help="Path to configuration file.")
    parser.add_argument("application", type=str, help="Application ID or " +
                        "key to match predefined application IDs.")
    parser.add_argument("query", type=str, help="Kusto query to run or key " +
                        "to match predefined query.")

    args = parser.parse_args(args)

    # Azure REST API URL
    api = "https://api.applicationinsights.io/"
    # api = "https://api.loganalytics.io/"

    # Instantiate Azure Kusto-client
    azure_client = AzureClient(args, api=api, kusto=True)

    # Match predefined queries
    query = args.query
    if azure_client.kusto_queries.get(query):
        query = azure_client.kusto_queries.get(query)

    # Match predefined application IDs
    application_id = args.application
    if azure_client.application_ids.get(application_id):
        application_id = azure_client.application_ids.get(application_id)

    # Post query
    response = azure_client.query(
        method="POST",
        json={"query": query},
        url="{}v1/apps/{}/query".format(api, application_id)
    )

    # Print response
    print(json.dumps(response))


if __name__ == "__main__":
    main()
