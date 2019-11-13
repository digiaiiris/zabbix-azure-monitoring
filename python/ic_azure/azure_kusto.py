#!/usr/bin/python

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
    parser.add_argument("query", type=str, help="Kusto query to run.")

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

    # Post query
    response = azure_client.post_query(
        json={"query": query},
        url="{}v1/apps/{}/query".format(api, azure_client.application_id)
    )

    # Print response
    print(json.dumps(response))


if __name__ == "__main__":
    main()
