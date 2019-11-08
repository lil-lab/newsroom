Installation Instructions
=========================

Newsroom requires Python 3.6+ and can be installed using `pip`:

```sh
pip install -e git+git://github.com/clic-lab/newsroom.git#egg=newsroom
```

Getting the Data
================

There are two ways to obtain the summaries dataset.
You may use the scripts described below to scrape the web pages used in the dataset and extract the summaries. 
Alternatively, the complete dataset is also available from [https://summari.es/download/](https://summari.es/download/).

Data Processing Tools
=====================

Newsroom contains two scripts for downloading and processing data downloaded from Archive.org. First, download the "Thin Dataset" from [https://summari.es/download/](https://summari.es/download/). 
(The "Data Builder" is this Python package.)
Download and extract `thin.tar` with `tar xvf thin.tar`, yielding directory `thin` containing several `.jsonl.gz` files.

Next, use `newsroom-scrape` and `newsroom-extract` to process the data, as described below.
Both of these tools have additional argument help pages when you use the `--help` command line option.

Data Scraping
-------------

The `thin` directory will contain three files, `train.jsonl.gz`, `dev.jsonl.gz` and `test.jsonl.gz`. To begin downloading the development set from Archive.org, run the following:

```sh
newsroom-scrape --thin thin/dev.jsonl.gz --archive dev.archive
```

Estimated download time is indicated with a progress bar. If errors occur during downloading, you may need to re-run the script later to capture the missing articles. This process is network bound and depends mostly on Archive.org, save your CPU cycles for the extraction stage!

The downloading process can be stopped at any time with `Control-C` and resumed later. It is also possible to perform extraction of a partially downloaded dataset with `newsroom-extract` before continuing to download the full version.

Data Extraction
---------------

The `newsroom-extract` tool extracts summaries and article text from the data downloaded by `newsroom-scrape`. This tool produces a new file that does not modify the original output file of `newsroom-scrape`, and can be run with:

```sh
newsroom-extract --archive dev.archive --dataset dev.dataset
```

The script automatically parallelizes extraction across your CPU cores. To disable this or reduce the number of cores used, use the `--workers` option. Like scraping, the extraction process can be stopped at any point with `Control-C` and resumed later.

Reading and Analyzing the Data
==============================

All data are represented using [gzip-compressed JSON lines][jsonl]. The Newsroom package provides an easy tool to read an write these files — and do so up to 20x faster than the standard Python `gz` and `json` packages!

```python
from newsroom import jsonl

# Read entire file:

with jsonl.open("train.dataset", gzip = True) as train_file:
    train = train_file.read()

# Read file entry by entry:

with jsonl.open("train.dataset", gzip = True) as train_file:
    for entry in train_file:
        print(entry["summary"], entry["text"])
```

[jsonl]: http://jsonlines.org/

Extraction Analysis
-------------------

The Newsroom package also contains scripts for identifying extractive fragments and computing metrics described in the paper: coverage, density, and compression.

```python
import random

from newsroom import jsonl
from newsroom.analyze import Fragments

with jsonl.open("train.dataset", gzip = True) as train_file:
    train = train_file.read()

# Compute stats on random training example:

entry = random.choice(train)
summary, text = entry["summary"], entry["text"]
fragments = Fragments(summary, text)

# Print paper metrics:

print("Coverage:",    fragments.coverage())
print("Density:",     fragments.density())
print("Compression:", fragments.compression())

# Extractive fragments oracle:

print("List of extractive fragments:")
print(fragments.strings())
```

Evaluation Tools
================

The Newsroom package contains a standardized way for running and scoring Docker-based summarization systems. For an example, see the `/example` directory for a Docker image of the TextRank system used in the paper.

The package also contains a script for producing tables similar to those in the paper for compression, coverage, and density. These tables are helpful for understanding your system's performance across different difficulties of text-summary pairs.

Running Your System
-------------------

After starting Docker and building your image (named "textrank" in the following examples), the system can be evaluated using the script:

```sh
newsroom-run \
    --system textrank \              # Name of Docker image.
    --dataset dev.dataset \          # Path to evaluation data.
    --summaries textrank.summaries \ # Output path to write system summaries.
    --keys text                      # JSON keys to feed Docker system.
```

The script runs your system Docker image, passes article text (and other requested metadata) into the container through standard input, expecting summaries to be supplied on standard output.

Scoring Your System
-------------------

To score your system, run the following:

```sh
newsroom-score \
    --dataset dev.dataset \          # Path to evaluation data.
    --summaries textrank.summaries \ # Path to system's output summaries.
    --scores textrank.scores \       # Output path to write summary scores.
    --rouge 1,2,L \                  # ROUGE variants to run.
    --unstemmed                      # Or, --stemmed for Porter stemming.
```

The script produces a file (`textrank.scores`) containing pairs of system and reference summaries, article metadata for analysis, and ROUGE scores. Additionally, overall ROUGE scores are printed on completion.

Producing Output Tables
-----------------------

To produce ROUGE tables across Newsroom compression, density, and coverage subsets, run the following:

```sh
newsroom-tables \
    --scores textrank.scores \
    --rouge 1,2,L \
    --variants fscore \
    --bins density,compression,coverage
```

All command line tools have a `--help` flag that show a description of arguments and their defaults.
