################################################################################

import json, bz2, click
from newsroom import jsonl

from tqdm import tqdm
from newsroom.analyze.rouge import perl

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

@click.option("--dataset",   type = articles_file,  required = True)
@click.option("--summaries", type = summaries_file, required = True)
@click.option("--scores",    type = output_file,    required = True)

@click.option("--rouge", type = str, default = "1,2,L")
@click.option('--stemmed/--unstemmed', default = False)

################################################################################

def main(dataset, summaries, scores, rouge, stemmed):

    rouges = rouge.upper().split(",")
    aggregate = {"ROUGE-" + r: [] for r in rouges}

    ROUGE_N, ROUGE_L = perl.ROUGE_N, perl.ROUGE_L

    with jsonl.open(dataset, gzip = True) as a:
        with jsonl.open(summaries, gzip = True) as s:
            with jsonl.open(scores, gzip = True) as f:

                # If scores file exists, delete it.
                # (So we write, rather than appending.)

                f.delete()

                dataset_size = len(s)

                progress = tqdm(
                    zip(a, s),
                    total = dataset_size,
                    desc  = "Evaluating"
                )

                for aline, sline in progress:

                    ref = aline["summary"]
                    sys = sline["system"]

                    results = {}

                    for rouge in rouges:

                        if rouge == "L":

                            result = ROUGE_L(ref, sys, stem = stemmed)

                        else:

                            try:

                                result = ROUGE_N(
                                    ref, sys,
                                    n = int(rouge),
                                    stem = stemmed)

                            except ValueError:

                                raise ValueError("Invalid ROUGE " + rouge)

                        for kind in ("precision", "recall", "fscore"):

                            results[f"rouge_{rouge}_{kind}"] = getattr(result, kind)
                            aggregate[f"ROUGE-{rouge}"].append(result)

                    results["reference"] = ref
                    results["system"] = sys

                    results.update({
                        k: v for k, v in aline.items()
                        if k not in ("text", "summary", "title")
                    })

                    f.appendline(results)

    print("\nScoring complete. Overall statistics:\n")
    for name, scores in aggregate.items():

        recall    = sum(s.recall    for s in scores) / len(scores) * 100
        precision = sum(s.precision for s in scores) / len(scores) * 100
        fscore    = sum(s.fscore    for s in scores) / len(scores) * 100

        print(name, "recall:",    round(recall,    4))
        print(name, "precision:", round(precision, 4))
        print(name, "fscore:",    round(fscore,    4))
        print()

    print("Next, run newsroom-tables for detailed statistics.")

################################################################################
