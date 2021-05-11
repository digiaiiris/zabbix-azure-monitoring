#!/usr/bin/python3

# Python imports
import json
import os
import requests
import sys

# Azure imports
import adal
from azure.identity import CertificateCredential
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.resource import ResourceManagementClient
from msrestazure.azure_cloud import AZURE_PUBLIC_CLOUD


class AzureClient(object):
    """ Azure API client class. """

    def __init__(self, args, api=None, queries=False):

        """ Initializes connection to Azure service. """

        # Reset configuration file path
        config_file = ""

        # Retrieve configuration file path
        if args.config.startswith("/"):
            config_file = args.config
        elif os.getenv("AZURE_CONFIG_PATH") is not None:
            config_file = os.path.join(
                os.getenv("AZURE_CONFIG_PATH"),
                args.config
            )
        else:
            config_file = os.path.join(
                "/etc/zabbix/scripts-config/zabbix-azure-monitoring",
                args.config
            )

        # Check if configuration file exists
        if not os.path.exists(config_file):
            raise ValueError("Configuration file not found: {}".format(
                config_file
            ))

        # Read configuration file
        try:
            with open(config_file) as fh:
                config = json.load(fh)
        except IOError:
            raise IOError("I/O error while reading configuration: {}".format(
                config_file
            ))

        # Azure specific settings
        self.api = AZURE_PUBLIC_CLOUD.endpoints.active_directory_resource_id
        self.login_endpoint = AZURE_PUBLIC_CLOUD.endpoints.active_directory

        # Set instance variables
        self.application_ids = {}  # Application IDs for Kusto queries.
        self.queries = {}  # Kusto or Log Analytics queries
        self.resources = {}  # Resources for easier access
        self.subscription_id = ""  # Azure Subscription ID
        self.timeout = 5  # Default timeout for queries
        self.workspace_ids = {}  # Workspace IDs for Log Analytics queries

        # Check configurations for necessary fields
        for item in ["client_id", "pemfile", "subscription_id", "tenant_id",
                     "thumbprint"]:
            if not config[item]:
                raise Exception("Configurations are missing {}.".format(item))

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

        # Retrieve necessary configurations
        self.subscription_id = config["subscription_id"]

        # Azure API URL for Kusto or Log Analytics queries
        if api:
            self.api = api

        # Retrieve application/workspace IDs and queries
        if queries:
            if config.get("application_ids"):
                self.application_ids = config.get("application_ids")
            if config.get("workspace_ids"):
                self.workspace_ids = config.get("workspace_ids")
            if config.get("kusto_queries"):
                self.queries = config.get("kusto_queries")

        # Check configuration for resources
        if config.get("resources"):
            self.resources = config.get("resources")

        # Check configuration for timeout
        if config.get("timeout"):
            self.timeout = config["timeout"]

        # Create authentication context
        context = adal.AuthenticationContext("{}/{}".format(
            self.login_endpoint,
            config["tenant_id"]
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
        self.credentials = CertificateCredential(
            config["tenant_id"],
            config["client_id"],
            config["pemfile"]
        )

    def client(self):
        """ Initializes new monitoring client for Azure services. """

        self._client = None

        # Instantiate new monitoring client
        self._client = MonitorManagementClient(
            self.credentials,
            self.subscription_id
        )

        return self._client

    def resource_client(self):
        """ Initializes new resource client for Azure services. """

        self._resource_client = None

        # Instantiate new resource client
        self._resource_client = ResourceManagementClient(
            self.credentials,
            self.subscription_id
        )

        return self._resource_client

    def query(self, method="GET", json=None, url=""):
        """ Run query to Azure REST APIs. """

        # Define request headers
        headers = {
            "Authorization": "Bearer {}".format(self.access_token),
            "Content-Type": "application/json"
        }

        # Declare variables
        response = None

        try:
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
                raise Exception("Invalid method. {}".format(method))
        except requests.exceptions.RequestException as e:
            print("There was an ambiguous exception that occurred while " +
                  "handling your request. {}".format(e))
            sys.exit()
        except requests.exceptions.ConnectionError as e:
            print("A Connection error occurred: {}".format(e))
            sys.exit()
        except requests.exceptions.HTTPError as e:
            print("An HTTP error occurred. {}".format(e))
            sys.exit()
        except requests.exceptions.URLRequired as e:
            print("A valid URL is required to make a request. {}".format(e))
            sys.exit()
        except requests.exceptions.TooManyRedirects as e:
            print("Too many redirects. {}".format(e))
            sys.exit()
        except requests.exceptions.ConnectTimeout as e:
            print("The request timed out while trying to connect to the " +
                  "remote server. {}".format(e))
            sys.exit()
        except requests.exceptions.ReadTimeout as e:
            print("The server did not send any data in the allotted amount " +
                  "of time. {}".format(e))
            sys.exit()
        except requests.exceptions.Timeout as e:
            print("The request timed out. {}".format(e))
            sys.exit()
        except Exception as e:
            print("Unknown exception occured: {}".format(e))
            sys.exit()

        # Check response before proceeding
        if not response:
            print("Unable to retrieve response.")
            sys.exit()

        # Check status code
        if response.status_code != 200:
            raise Exception("Status code error: {}, status code: {}".format(
                response.text,
                response.status_code
            ))

        # Return JSON response
        return response.json()


if __name__ == "__main__":
    pass
