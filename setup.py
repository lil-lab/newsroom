from setuptools import setup, find_packages
from os import system

setup(
    name = "newsroom",
    version = "0.1",
    packages = find_packages(),
    include_package_data = True,

    install_requires = [
        "beautifulsoup4==4.6.0",
        "click==6.7",
        "nltk==3.2.5",
        "readability-lxml==0.6.2",
        "requests==2.18.4",
        "tqdm==4.15.0",
        "numpy==1.13.3",
        "ujson==1.35",
        "spacy==2.0.4",
    ],

    entry_points = {
        "console_scripts": [
            "newsroom-scrape=newsroom.build.scrape:main",
            "newsroom-extract=newsroom.build.extract:main",
        ]
    }
)

system("python -m spacy download en_core_web_sm-2.0.0 --direct")
