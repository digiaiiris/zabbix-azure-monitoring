#!/usr/bin/python

# Python imports
import os
from setuptools import setup

setup(
    name="azure-monitoring",
    version="1.7.0",
    author="Antti-Pekka Meronen",
    author_email="antti-pekka.meronen@digia.com",
    description="Monitoring scripts for Azure services",
    url="https://github.com/digiaiiris/zabbix-azure-monitoring/",
    license="GPLv3",
    packages=["ic_azure"],
    entry_points={
        "console_scripts": [
            "azure_discover_resources = ic_azure.azure_discover_resources:main",
            "azure_discover_metrics = ic_azure.azure_discover_metrics:main",
            "azure_discover_roles = ic_azure.azure_discover_roles:main",
            "azure_logic_apps = ic_azure.azure_kusto:main",
            "azure_kusto = ic_azure.azure_kusto:main",
            "azure_metric = ic_azure.azure_metric:main"
        ]
    },
    install_requires=[
        'adal>=1.2.1',
        'azure>=4.0.0',
        'requests>=2.22.0'
    ]
)
