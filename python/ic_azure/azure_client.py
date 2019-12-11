#!/usr/bin/python

# Python imports
import datetime
import errno
import json
import os
import requests
import sys

# Azure imports
import adal
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.resource import ResourceManagementClient
from msrestazure.azure_active_directory import AADTokenCredentials
from msrestazure.azure_cloud import AZURE_PUBLIC_CLOUD


class AzureClient(object):
    """Azure API client class."""

    def __init__(self, args, api=None, kusto=False):
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

        # Set instance variables
        self.api = AZURE_PUBLIC_CLOUD.endpoints.active_directory_resource_id
        self.application_id = config["application_id"]
        self.subscription_id = config["subscription_id"]

        # Azure API URL (for Kusto queries)
        if api:
            self.api = api

        # Set Kusto queries array
        if kusto:
            self.kusto_queries = {}
            if config.get("kusto_queries"):
                self.kusto_queries = config.get("kusto_queries")

        # Set resources array
        self.resources = {}
        if config.get("resources"):
            self.resources = config.get("resources")

        # Set script timeout
        if config.get("timeout"):
            self.timeout = config["timeout"]
        else:
            self.timeout = 5

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

        # Acquire token with client certificate
        management_token = context.acquire_token_with_client_certificate(
            self.api,
            config["client_id"],
            config["key"],
            config["thumbprint"]
        )

        # Grab access token
        self.access_token = management_token.get("accessToken")

        # Create credentials object
        self.credentials = AADTokenCredentials(
            management_token,
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

    def query(self, method="GET", json=None, url=""):
        """Run query to Azure REST APIs."""

        try:
            # Define request headers
            headers = {
                "Authorization": "Bearer {}".format(self.access_token),
                "Content-Type": "application/json"
            }

            # Do request
            if method == "GET":
                response = requests.get(
                    headers=headers,
                    json=json,
                    timeout=self.timeout,
                    url=url
                )
            elif method == "POST":
                response = requests.post(
                    headers=headers,
                    json=json,
                    timeout=self.timeout,
                    url=url
                )
            else:
                print("Invalid method. {}".format(method))
                sys.exit(1)
        except requests.exceptions.RequestException as e:
            print("There was an ambiguous exception that occurred while " +
                  "handling your request. {}".format(e))
            sys.exit(1)
        except requests.exceptions.ConnectionError as e:
            print("A Connection error occurred: {}".format(e))
            sys.exit(1)
        except requests.exceptions.HTTPError as e:
            print("An HTTP error occurred. {}".format(e))
            sys.exit(1)
        except requests.exceptions.URLRequired as e:
            print("A valid URL is required to make a request. {}".format(e))
            sys.exit(1)
        except requests.exceptions.TooManyRedirects as e:
            print("Too many redirects. {}".format(e))
            sys.exit(1)
        except requests.exceptions.ConnectTimeout as e:
            print("The request timed out while trying to connect to the " +
                  "remote server. {}".format(e))
            sys.exit(1)
        except requests.exceptions.ReadTimeout as e:
            print("The server did not send any data in the allotted amount " +
                  "of time. {}".format(e))
            sys.exit(1)
        except requests.exceptions.Timeout as e:
            print("The request timed out. {}".format(e))
            sys.exit(1)

        # Check HTTP status code
        if response.status_code != 200:
            print("HTTP status code error. {}".format(response.status_code))
            sys.exit(1)

        # Return JSON response
        return response.json()


if __name__ == "__main__":
    pass
