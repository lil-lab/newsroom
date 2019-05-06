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

submission_file = click.Path(
    exists       = False,
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
    "--submission",
    type = submission_file,
    default = "submission.csv",
    help = "Output path to Kaggle CSV. [default = submission.csv]"
)

@click.option(
    "--rouge",
    type = str,
    default = "1",
    help = "ROUGE variant to use. [default = 1]"
)

@click.option(
    "--variant",
    type = str,
    default = "fscore",
    help = "ROUGE score variant to use. [default = fscore]"
)

################################################################################

def main(scores, submission, rouge, variant):

    df = pd.DataFrame(jsonl.gzread(scores))

    rouge_score = df[f"rouge_{rouge}_{variant}"].mean()
    hack_score = (1 - rouge_score ** 2) ** (1/2) - 1 
    csv = f"Id,Predicted\n1,{hack_score}\n2,{rouge_score}"

    with open(submission, "w") as f:
        f.write(csv)

################################################################################
