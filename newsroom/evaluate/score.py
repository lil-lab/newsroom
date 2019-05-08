################################################################################

import json, bz2, click
from newsroom import jsonl

from tqdm import tqdm
from newsroom.analyze.rouge import ROUGE_N, ROUGE_L

from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor

from .compute_rouge import *

################################################################################

articles_file = click.Path(
    exists       = True,
    dir_okay     = False,
    readable     = True,
    resolve_path = True,
)

summaries_file = click.Path(
    exists       = True,
    dir_okay     = False,
    readable     = True,
    resolve_path = True,
)

output_file = click.Path(
    exists       = False,
    dir_okay     = False,
    writable     = True,
    resolve_path = True,
)

################################################################################

@click.command()

@click.option(
    "--dataset",
    type = articles_file,
    required = True,
    help = "Input path to full dataset."
)

@click.option(
    "--summaries",
    type = summaries_file,
    required = True,
    help = "Input path to system summary output."
)

@click.option(
    "--scores",
    type = output_file,
    required = True,
    help = "Output path for system evaluation."
)

@click.option(
    "--rouge",
    type = str,
    default = "1,2,L",
    help = "List of ROUGE types to use. [default = 1,2,L]"
)

@click.option(
    "--stemmed/--unstemmed",
    default = False,
    help = "Turn on or off Porter stemming. [default = off]"
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

def main(dataset, summaries, scores, rouge, stemmed, workers, chunksize):

    rouges = rouge.upper().split(",")

    with jsonl.open(dataset, gzip = True) as a:
        with jsonl.open(summaries, gzip = True) as s:
            with jsonl.open(scores, gzip = True) as f:

                # If scores file exists, delete it.
                # (So we write, rather than appending.)

                f.delete()
                size = len(s)
                chunk = []

                with tqdm(total = size, desc = "Evaluating") as progress:

                    def process_chunk():

                        with ProcessPoolExecutor(workers) as ex:

                            results = list(ex.map(compute_rouge, chunk))

                            f.append(results)
                            progress.update(len(results))

                    for aline, sline in zip(a, s):

                        chunk.append([aline, sline, rouges, stemmed])

                        if len(chunk) >= chunksize:

                            process_chunk()
                            chunk = []

                    process_chunk()

    aggregate = {}
    with jsonl.open(scores, gzip = True) as f:

        for entry in f:
            for k, v in entry.items():

                if not k.startswith("rouge_"):
                    continue

                if k not in aggregate:
                    aggregate[k] = []
                else:
                    aggregate[k].append(v)

    print("\nScoring complete. Overall statistics:\n")
    for name, scores in aggregate.items():

        pretty = name \
            .title() \
            .replace("_", " ") \
            .replace("Rouge ", "ROUGE-") \
            .replace("Fscore", "F-Score:  ") \
            .replace("Precision", "Precision:") \
            .replace("Recall", "Recall:   ")

        print(pretty, round(sum(scores) / len(scores) * 100, 4))

    print()
    print("Next, run newsroom-tables for detailed statistics.")

################################################################################
