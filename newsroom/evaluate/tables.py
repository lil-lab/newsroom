################################################################################

import json, bz2, click
from newsroom import jsonl
import pandas as pd

################################################################################

scores_file = click.Path(
    exists       = True,
    dir_okay     = False,
    readable     = True,
    resolve_path = True,
)

################################################################################

@click.command()

@click.option(
    "--scores",
    type = scores_file,
    required = True,
    help = "Input path to system scored summaries."
)

@click.option(
    "--rouge",
    type = str,
    default = "1,2,L",
    help = "List of ROUGE types to show. [default = 1,2,L]"
)

@click.option(
    "--variants",
    type = str,
    default = "precision,recall,fscore",
    help = "List of ROUGE score variants to show. [default = precision,recall,fscore]"
)

@click.option(
    "--bins",
    type = str,
    default = "density,coverage,compression",
    help = "List of summary bins to aggregate across. [default = density,coverage,compression]"
)

################################################################################

def main(scores, rouge, variants, bins):

    bins     = [f"{b.title()} Bin" for b in bins.split(",")]
    rouge    = [f"ROUGE {r}" for r in rouge.split(",")]
    variants = [v.title().replace("Fscore", "F-Score") for v in variants.split(",")]

    df = pd.DataFrame(jsonl.gzread(scores))

    df.columns = [
        column
        .title()
        .replace("Rouge", "ROUGE")
        .replace("_", " ")
        .replace("Fscore", "F-Score")
        for column in df.columns
    ]

    for r in rouge:

        for b in bins:

            rouge_variants = [r + " " + v for v in variants]
            print(df.groupby(b)[rouge_variants].mean() * 100)
            print()

################################################################################
