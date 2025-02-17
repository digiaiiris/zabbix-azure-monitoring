#!/usr/bin/env python

# Python imports
import json as jsonlib
import os
import requests
import sys

# 3rd-party imports
import msal
import OpenSSL

from azure.identity import CertificateCredential
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.resource import ResourceManagementClient


class AzureClient:
    """ Azure API client class. """

    def __init__(self, args: dict, api: str = None, queries: bool = False) -> None:

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
                "/opt/digiaiiris/zabbix-agent/scripts-config/zabbix-azure-monitoring",
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
                config = jsonlib.load(fh)
        except IOError:
            raise IOError("I/O error while reading configuration: {}".format(
                config_file
            ))

        # Azure specific settings
        self.api = "https://management.core.windows.net/"
        self.login_endpoint = "https://login.microsoftonline.com"

        # Set instance variables
        self.application_ids = {}  # Application IDs for Kusto queries.
        self.queries = {}  # Kusto or Log Analytics queries
        self.resources = {}  # Resources for easier access
        self.subscription_id = ""  # Azure Subscription ID
        self.timeout = 5  # Default timeout for queries
        self.workspace_ids = {}  # Workspace IDs for Log Analytics queries

        # Check configurations for necessary fields
        for item in ["client_id", "pemfile", "subscription_id", "tenant_id"]:
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

        # Check if certificate file exists
        if not os.path.exists(config["pemfile"]):
            sys.exit("Certificate file does not exist.")

        # Read certificate file
        with open(config["pemfile"], "rb") as fh:
            certificate_str = fh.read()

        # Load certificate and generate thumbprint
        certificate = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, certificate_str)
        thumbprint = certificate.digest("sha1").decode("utf-8")

        # Load private key
        private_key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, certificate_str)

        # Create confidential client app instance
        app = msal.ConfidentialClientApplication(
            config["client_id"],
            authority=f'{self.login_endpoint}/{config["tenant_id"]}',
            client_credential={
                "thumbprint": thumbprint.replace(":", ""),
                "private_key": private_key.to_cryptography_key()
            }
        )

        # Acquire token
        response = app.acquire_token_for_client(
            scopes=[f"{self.api}/.default"]
        )

        # Check if response has token
        if "access_token" in response:
            self.access_token = response["access_token"]
        else:
            sys.exit("Token missing from response.")

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
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        # Declare variables
        response = None

        # Try to run request
        try:
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
        except requests.exceptions.ConnectTimeout as ex:
            sys.exit(f"The request timed out while trying to connect to the remote server. {ex}")
        except requests.exceptions.ReadTimeout as ex:
            sys.exit(f"The server did not send any data in the allotted amount of time. {ex}")
        except requests.exceptions.ConnectionError as ex:
            sys.exit(f"A Connection error occurred: {ex}")
        except requests.exceptions.HTTPError as ex:
            sys.exit(f"An HTTP error occurred. {ex}")
        except requests.exceptions.Timeout as ex:
            sys.exit(f"The request timed out. {ex}")
        except requests.exceptions.TooManyRedirects as ex:
            sys.exit(f"Too many redirects. {ex}")
        except requests.exceptions.URLRequired as ex:
            sys.exit(f"A valid URL is required to make a request. {ex}")
        except requests.exceptions.RequestException as ex:
            sys.exit(
                f"There was an ambiguous exception that occurred while handling your request. {ex}"
            )
        except Exception as ex:
            sys.exit(f"Unknown exception occured: {ex}")

        # Check status code
        if hasattr(response, "status_code"):
            if response.status_code != 200:
                raise Exception("Status code error: {}, status code: {}".format(
                    response.text,
                    response.status_code
                ))

        # Check response before proceeding
        if not response:
            sys.exit("Unable to retrieve response.")

        # Return JSON response
        return response.json()


if __name__ == "__main__":
    pass
