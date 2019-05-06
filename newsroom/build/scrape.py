################################################################################

import click
import os.path

from tqdm import tqdm

from . import Downloader
from newsroom import jsonl

import random

################################################################################

def _exactness(url, amount):

    amount = max(1, amount)

    before, *after = url.split("id_/")
    *root, date = before.split("/")

    date = date[:amount]

    before = "/".join(root + [date])
    return "id_/".join([before] + after)

################################################################################

urls_file = click.Path(
    exists       = True,
    dir_okay     = False,
    readable     = True,
    writable     = True,
    resolve_path = True,
)

archive_file = click.Path(
    dir_okay     = False,
    readable     = True,
    writable     = True,
    resolve_path = True,
)

################################################################################

@click.command()

@click.option(
    "--urls",
    type = urls_file,
    help = "Input path to URL list of articles to download.",
)

@click.option(
    "--thin",
    type = urls_file,
    help = "Input path to \"thin\" template dataset.",
)

@click.option(
    "--archive",
    type = archive_file,
    required = True,
    help = "Output path to write raw article HTML.",
)

@click.option(
    "--exactness",
    type = int,
    default = None,
    help = "Exactness value. [see README]",
)

@click.option(
    "--workers",
    type = int,
    default = 16,
    help = "Number of threads to use. [default = 16]",
)

@click.option(
    "--tries",
    type = int,
    default = 3,
    help = "Download attempts per article. [default = 3]",
)

@click.option(
    "--sleep",
    type = float,
    default = 2,
    help = "Delay between downloading articles. [default = 2 sec]",
)

@click.option(
    "--multiplier",
    type = float,
    default = 1.5,
    help = "Archive.org rate limiting sensitivity. [default = 1.5]",
)

@click.option(
    "--diff",
    is_flag = True,
    help = "Check remaining URLs to download. [default = off]",
)

################################################################################

def main(urls, thin, archive, exactness, diff, **downloader_args):

    if not urls and not thin:

        print("Either --urls or --thin must be defined.")
        return

    # If the archive file exists, only download what we need.
    # Open the file and read all previously downloaded URLs.

    if not os.path.isfile(archive):

        done = {}

    else:

        print("Loading previously downloaded summaries:", end = " ")

        with jsonl.open(archive, gzip = True) as f:

            done = {ln["archive"] for ln in f}
            print(len(done), "downloaded summaries...", end = " ")

    # Read the URL file or thin.

    if urls:

        with open(urls, "r") as f:

            urls = [ln.strip() for ln in f]

    elif thin:

        with jsonl.open(thin, gzip = True) as f:

            urls = [entry["archive"] for entry in f]

    # Which URLs are remaining?

    todo = [url for url in urls if url not in done]
    size = round(0.00002 * len(todo), 1)

    # If --diff argument is enabled, just print undownloaded article URLs.

    if diff:

        print("there are", len(todo), "URLs not downloaded:\n")

        for url in todo:
            print(url)

        return

    else:

        print(len(todo), "new summaries (about", size, "GB).")

    # Truncate url dates if they can't be downloaded.

    if exactness is not None:

        exactness_map = {_exactness(url, exactness): url for url in todo}
        todo = list(exactness_map.keys())

    # Randomize todo to prevent "hard" pages from collecting at start.

    random.shuffle(todo)

    # Initialize the Archive scraper to start downloading.

    print("If pages fail to download now, re-run script when finished.\n")

    scraper = Downloader(**downloader_args)
    downloads = scraper.download(todo)

    # Progress bar arguments.

    progress = tqdm(
        total = len(todo),
        desc = "Downloading Summaries"
    )

    # Append the downloaded files to the compressed file.
    # (We checked earlier, so we won't overwrite older downloads.)

    errors = 0
    progress.update(0)

    try:

        with jsonl.open(archive, gzip = True) as f:

            for article in downloads:

                if article is None:

                    errors += 1

                    if errors % 10 == 0:

                        print()
                        print(errors, "pages need re-downloading later.")

                else:

                    # Rename url -> archive for consistency.

                    article["archive"] = article["url"]
                    del article["url"]

                    # Keep track of how much this article was truncated.

                    if exactness is not None:

                        exactness_archive = article["archive"]
                        real_archive = exactness_map[exactness_archive]

                        article["exactness_factor"] = exactness
                        article["exactness_archive"] = exactness_archive
                        article["archive"] = real_archive

                    # Write updated dictionary to JSON file.

                    f.appendline(article)

                progress.update(1)

        if errors > 0:

            print("\n\nRerun the script:", errors, "pages failed to download.")
            print("- Try running with a lower --workers count (default = 16).")
            print("- Check which URLs are left with the --diff flag.")
            print("- Last resort: --exactness X to truncate dates to X digits.")
            print("  (e.g., --exactness 4 will download the closest year.)")

        else:

            print("\n\nDownload complete. Next, run newsroom-extract.")

    except KeyboardInterrupt:

        print("\n\nDownload aborted with progress preserved.")
        print("Run script again to resume from this point.")

################################################################################

