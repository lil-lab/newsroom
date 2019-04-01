Installation Instructions
=========================

Newsroom requires Python 3 and can be installed using `pip`:

```sh
pip install -e git+git://github.com/clic-lab/newsroom.git#egg=newsroom
```

Getting the Data
================

There are two ways to obtain the summaries dataset. You may use the scripts 
described below to scrape the web pages used in the dataset and extract the summaries. 
Alternatively, the data is also available from 
[https://summari.es/download/](https://summari.es/download/).

Data Processing Tools
=====================

Newsroom contains two scripts for downloading and processing data downloaded
from Archive.org. First, download the "thin" data from [summari.es][summaries]:

```sh
wget https://summari.es/files/thin.tar
tar xvf thin.tar
```

Both the `newsroom-scrape` and `newsroom-extract` tools described below have
argument help pages accessed with the `--help` command line option.

[summaries]: https://summari.es/


Data Scraping
-------------

The `thin` directory will contain three files, `train.jsonl.gz`, `dev.jsonl.gz`
and `test.jsonl.gz`. To begin downloading the development set from Archive.org,
run the following:

```sh
newsroom-scrape --thin thin/dev.jsonl.gz --archive dev.archive
```

Estimated download time is indicated with a progress bar. If errors occur during
downloading, you may need to re-run the script later to capture the missing
articles. This process is network bound and depends mostly on Archive.org, save
your CPU cycles for the extraction stage!

The downloading process can be stopped at any time with `Control-C` and resumed
later. It is also possible to perform extraction of a partially downloaded
dataset with `newsroom-extract` before continuing to download the full version.

Data Extraction
---------------

The `newsroom-extract` tool extracts summaries and article text from the data
downloaded by `newsroom-scrape`. This tool produces a new file that does not
modify the original output file of `newsroom-scrape`, and can be run with:

```sh
newsroom-extract --archive dev.archive --dataset dev.data
```

The script automatically parallelizes extraction across your CPU cores. To
disable this or reduce the number of cores used, use the `--workers` option.
Like scraping, the extraction process can be stopped at any point with
`Control-C` and resumed later.

Reading and Analyzing the Data
==============================

All data are represented using [gzip-compressed JSON lines][jsonl]. The Newsroom
package provides an easy tool to read an write these files — and do so up to
20x faster than the standard Python `gz` and `json` packages!

```python
from newsroom import jsonl

# Read entire file:

with jsonl.open("train.data", gzip = True) as train_file:
    train = train_file.read()

# Read file entry by entry:

with jsonl.open("train.data", gzip = True) as train_file:
    for entry in train_file:
        print(entry["summary"], entry["text"])
```

[jsonl]: http://jsonlines.org/

Extraction Analysis
-------------------

The Newsroom package also contains scripts for identifying extractive fragments
and computing metrics described in the paper: coverage, density, and compression.

```python
import random

from newsroom import jsonl
from newsroom.analyze import Fragments

with jsonl.open("train.data", gzip = True) as train_file:
    train = train_file.read()

# Compute stats on random training example:

entry = random.choice(train)
summary, text = train[0]["summary"], train[0]["text"]
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

Available soon!
