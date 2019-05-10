from setuptools import setup, find_packages
from setuptools.command.install import install
from glob import glob

from os import system

class installwrap(install):

    def run(self):

        install.run(self)

        try: system("python -m spacy download en_core_web_sm")
        except: pass

        try: system("apt-get install -y libxml-parser-perl")
        except: pass


setup(
    name = "newsroom",
    version = "0.1",
    packages = find_packages(),
    include_package_data = True,

    install_requires = [
        "beautifulsoup4>=4.6.0",
        "click>=6.7",
        "nltk>=3.2",
        "numpy>=1.13.3",
        "pandas>=0.23",
        "pyrouge>=0.1.3",
        "readability-lxml>=0.6.2",
        "requests>=2.18.4",
        "spacy>=2.0.4",
        "tqdm>=4.15.0",
        "ujson>=1.35",
    ],

    entry_points = {
        "console_scripts": [
            "newsroom-scrape=newsroom.build.scrape:main",
            "newsroom-extract=newsroom.build.extract:main",
            "newsroom-run=newsroom.evaluate.run:main",
            "newsroom-score=newsroom.evaluate.score:main",
            "newsroom-tables=newsroom.evaluate.tables:main",
            "newsroom-kaggle=newsroom.evaluate.kaggle:main",
        ]
    },

    cmdclass = {
        "install": installwrap,
    },

)
