#!/usr/bin/python3

# Python imports
import os
from setuptools import setup

setup(
    name="azure-monitoring",
    version="1.9.3",
    author="Antti-Pekka Meronen",
    author_email="antti-pekka.meronen@digia.com",
    description="Monitoring scripts for Azure services",
    url="https://github.com/digiaiiris/zabbix-azure-monitoring/",
    license="GPLv3",
    packages=["ic_azure"],
    entry_points={
        "console_scripts": [
            "azure_discover_resources=ic_azure.azure_discover_resources:main",
            "azure_discover_metrics=ic_azure.azure_discover_metrics:main",
            "azure_discover_roles=ic_azure.azure_discover_roles:main",
            "azure_logic_apps=ic_azure.azure_logic_apps:main",
            "azure_metric=ic_azure.azure_metric:main",
            "azure_query=ic_azure.azure_query:main"
        ]
    },
    install_requires=[
        'adal>=1.2.5',
        'azure-identity>=1.4.1',
        'azure-mgmt-monitor>=2.0.0',
        'azure-mgmt-resource>=15.0.0',
        'msrestazure>=0.6.4',
        'requests>=2.24.0'
    ]
)
