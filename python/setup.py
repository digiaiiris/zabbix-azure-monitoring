#!/usr/bin/python

# Python imports
import os
from setuptools import setup

setup(
    name="azure-monitoring",
    version="1.1.1",
    author="Antti-Pekka Meronen",
    author_email="antti-pekka.meronen@digia.com",
    description="Monitoring scripts for Azure services",
    url="https://github.com/digiaiiris/zabbix-azure-monitoring/",
    license="GPLv3",
    packages=["ic_azure"],
    entry_points={
        "console_scripts": [
            "azure_discovery = ic_azure.azure_discovery:main",
            "azure_metric = ic_azure.azure_metric:main"
        ]
    },
    install_requires=[
        'adal>=1.2.1',
        'azure>=4.0.0'
    ]
)
