################################################################################

from tqdm import tqdm

import click, os
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor

from . import Article

from newsroom import jsonl
from newsroom.analyze import Fragments

################################################################################

archive_file = click.Path(
    exists       = True,
    dir_okay     = False,
    readable     = True,
    resolve_path = True,
)

dataset_file = click.Path(
    dir_okay     = False,
    readable     = True,
    writable     = True,
    resolve_path = True,
)

################################################################################

cutoffs = {
    "coverage":    (0.7857142857, 0.9444444444),
    "density":     (1.5, 8.1875),
    "compression": (15.5, 35.4285714286),
}

levels = {
    "coverage":    ("low", "medium", "high"),
    "density":     ("abstractive", "mixed", "extractive"),
    "compression": ("low", "medium", "high"),
}

def binner(value, cutoffs, levels):

    for c, cut in enumerate(cutoffs):
        if value <= cut:
            return levels[c]

    return levels[-1]

################################################################################

@click.command()

@click.option(
    "--archive",
    type = archive_file,
    default = None,
    help = "Input path to dataset of raw article HTML."
)

@click.option(
    "--urldiff",
    type = archive_file,
    default = None,
    help = "Input path to check remaining URLs to download."
)

@click.option(
    "--dataset",
    type = dataset_file,
    required = True,
    help = "Output path for final dataset.",
)

@click.option(
    "--workers",
    type = int,
    default = cpu_count(),
    help = "Number of processes to use. [default = CPU count]",
)

@click.option(
    "--chunksize",
    type = int,
    default = cpu_count() * 20,
    help = "Items processed between updates. [default = 20*CPUs]",
)

################################################################################

def main(archive, urldiff, dataset, workers, chunksize):

    if archive is None and urldiff is None:

        print("One of --archive or --urldiff required.")

        return

    elif urldiff:

        # Check to see if the dataset contains all URLs.

        required = set()

        print("Comparing URL file to dataset...")

        with open(urldiff, "rt") as urls_file:

            for line in urls_file:
                required.add(line.strip())

        with jsonl.open(dataset, gzip = True) as dataset_file:

            for article in dataset_file.readlines(ignore_errors = True):

                url = article.get("archive", article.get("url"))
                required.discard(url)

        if len(required) > 0:

            print(len(required), "URLs missing:\n")

            for url in required:

                print(url)

        else:

            print("Dataset complete.")

        return

    previously = set()
    todo = set()

    if os.path.isfile(dataset):

        print("Comparing archive and dataset files: ", end = "")

        with jsonl.open(dataset, gzip = True) as dataset_file:

            for article in dataset_file.readlines(ignore_errors = True):

                url = article.get("archive", article.get("url"))
                previously.add(url)

        print("found", len(previously), "finished summaries... ", end = "")

    else:

        print("Loading downloaded summaries: ", end = "")

    with jsonl.open(archive, gzip = True) as archive_file:

        for article in archive_file.readlines(ignore_errors = True):

            url = article.get("archive", article.get("url"))
            todo.add(url)

    todo -= previously

    print("found", len(todo), "new summaries.\n")

    with tqdm(total = len(todo), desc = "Extracting Summaries") as progress:
        with jsonl.open(archive, gzip = True) as archive_file:
            with jsonl.open(dataset, gzip = True) as dataset_file:

                chunk = []

                def process_chunk():

                    with ProcessPoolExecutor(workers) as ex:

                        results = list(ex.map(Article.process, chunk))
                        results = [r for r in results if r is not None]

                        # Compute statistics.

                        for result in results:

                            if result["text"] is None or result["summary"] is None: continue

                            fragments = Fragments(result["summary"], result["text"])

                            result["density"] = fragments.density()
                            result["coverage"] = fragments.coverage()
                            result["compression"] = fragments.compression()

                            result["compression"] = fragments.compression()
                            result["coverage"] = fragments.coverage()
                            result["density"] = fragments.density()

                            for measure in ("compression", "coverage", "density"):

                                result[measure + "_bin"] = binner(
                                    result[measure],
                                    cutoffs[measure],
                                    levels[measure])

                        dataset_file.append(results)
                        progress.update(len(results))

                for article in archive_file.readlines(ignore_errors = True):

                    url = article.get("archive", article.get("url"))
                    if url not in todo: continue

                    chunk.append(article)

                    if len(chunk) >= chunksize:

                        process_chunk()
                        chunk = []

                process_chunk()

    print("\nExtraction complete.")

################################################################################
