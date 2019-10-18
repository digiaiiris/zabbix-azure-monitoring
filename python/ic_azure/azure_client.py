#!/usr/bin/python

# Python imports
import datetime
import errno
import json
import os
import requests

# Azure imports
import adal
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.resource import ResourceManagementClient
from msrestazure.azure_active_directory import AADTokenCredentials
from msrestazure.azure_cloud import AZURE_PUBLIC_CLOUD


class AzureClient(object):
    """Azure API client class."""

    def __init__(self, args, api=None):
        """Initializes connection to Azure service."""

        # Check if configuration file exists
        if not os.path.exists(args.config):
            raise Exception("Configuration file not found: {}".format(
                            args.config))

        # Read configuration file
        try:
            with open(args.config) as fh:
                config = json.load(fh)
        except IOError:
            raise Exception("I/O error while reading configuration: {}".format(
                args.config
            ))

        # Set class variables from configuration file
        self.application_id = config["application_id"]
        self.subscription_id = config["subscription_id"]

        # Create authentication context
        login_endpoint = AZURE_PUBLIC_CLOUD.endpoints.active_directory
        context = adal.AuthenticationContext("{}/{}".format(
            login_endpoint,
            config["tenant_id"]
        ))

        # Check if PEM-file exists
        if not os.path.exists(config["pemfile"]):
            raise Exception("PEM-file not found: {}".format(config["pemfile"]))

        # Read PEM-file
        try:
            with open(config["pemfile"], "r") as file:
                config["key"] = file.read()
        except IOError:
            raise Exception("I/O error while reading PEM-file: {}".format(
                config["pemfile"]
            ))

        # If Azure API URL was not provided, use default AD resource
        if api:
            self.api = api
        else:
            self.api = AZURE_PUBLIC_CLOUD.endpoints.active_directory_resource_id

        # Acquire token with client certificate
        self.management_token = context.acquire_token_with_client_certificate(
            self.api,
            config["client_id"],
            config["key"],
            config["thumbprint"]
        )

        # Create credentials object
        self.credentials = AADTokenCredentials(
            self.management_token,
            config["client_id"]
        )

    def client(self):
        """Initializes new monitoring client for Azure services."""

        self._client = None

        # Instantiate new monitoring client
        self._client = MonitorManagementClient(
            self.credentials,
            self.subscription_id
        )

        return self._client

    def resource_client(self):
        """Initializes new resource client for Azure services."""

        self._resource_client = None

        # Instantiate new resource client
        self._resource_client = ResourceManagementClient(
            self.credentials,
            self.subscription_id
        )

        return self._resource_client

    def kusto_query(self, query):
        """Initializes new Kusto-query client for Azure services."""

        response = requests.post(
            headers = {
                "Authorization": "Bearer {}".format(
                    self.management_token.get("accessToken")),
                "Content-Type": "application/json"
            },
            json = { "query": query },
            url = "{}v1/apps/{}/query".format(self.api, self.application_id)
        )

        return response.json()

if __name__ == "__main__":
    pass
