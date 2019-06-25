#!/usr/bin/python

# Python imports
import datetime
import errno
import json
import os

# Azure imports
import adal
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.resource import ResourceManagementClient
from msrestazure.azure_active_directory import AADTokenCredentials
from msrestazure.azure_cloud import AZURE_PUBLIC_CLOUD


class AzureClient(object):
    """Azure API client class."""

    def __init__(self, args):
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
        self.subscription_id = config["subscription_id"]

        # Create authentication context
        login_endpoint = AZURE_PUBLIC_CLOUD.endpoints.active_directory
        resource = AZURE_PUBLIC_CLOUD.endpoints.active_directory_resource_id
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

        # Acquire token with client certificate
        management_token = context.acquire_token_with_client_certificate(
            resource,
            config["application_id"],
            config["key"],
            config["thumbprint"]
        )

        # Create credentials object
        self.credentials = AADTokenCredentials(
            management_token,
            config["application_id"]
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


if __name__ == "__main__":
    pass
