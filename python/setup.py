#!/usr/bin/python3

# Python imports
import os
from setuptools import setup

setup(
    name="azure-monitoring",
    version="1.24",
    author="Antti-Pekka Meronen",
    author_email="antti-pekka.meronen@digia.com",
    description="Monitoring scripts for Azure services",
    url="https://github.com/digiaiiris/zabbix-azure-monitoring/",
    license="GPLv3",
    packages=["ic_azure"],
    entry_points={
        "console_scripts": [
            "azure_discover_dimensions=ic_azure.azure_discover_dimensions:main",
            "azure_discover_resources=ic_azure.azure_discover_resources:main",
            "azure_discover_metrics=ic_azure.azure_discover_metrics:main",
            "azure_discover_webapp_instances=ic_azure.azure_discover_webapp_instances:main",
            "azure_logic_apps=ic_azure.azure_logic_apps:main",
            "azure_metric=ic_azure.azure_metric:main",
            "azure_query=ic_azure.azure_query:main"
        ]
    },
    python_requires=">=3.11",
    install_requires=[
        "azure-identity",
        "azure-mgmt-monitor",
        "azure-mgmt-resource",
        "cryptography",
        "msal-extensions",
        "msrest",
        "requests"
    ]
)
