#!/usr/bin/python

# Python imports
import os
from setuptools import setup

setup(
    name="azure-monitoring",
    version="1.0.0",
    author="Antti-Pekka Meronen",
    author_email="antti-pekka.meronen@digia.com",
    description="Monitoring scripts for Azure services",
    url="https://github.com/digiaiiris/zabbix-azure-monitoring/",
    license="GPLv3",
    packages=["ic_azure"],
    entry_points={
        "console_scripts": [
            "azure_insights_discovery = ic_azure.insights_discovery:main",
            "azure_insights_metric = ic_azure.insights_metric:main"
        ]
    },
    install_requires=[
        'adal>=1.2.1',
        'azure>=4.0.0'
    ]
)
