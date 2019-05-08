################################################################################

from subprocess import Popen, PIPE, STDOUT
from threading import Thread
import bz2, json, click
from newsroom import jsonl

from . import readiter

from tqdm import tqdm

################################################################################

def _writer(process, dataset_file, keys):

    for article in dataset_file:

        subset = {k: article[k] for k in keys if k in article}
        encoded = json.dumps(subset).encode("utf-8")

        process.stdin.write(encoded + b"\n")

    process.stdin.close()

################################################################################

articles_file = click.Path(
    exists       = True,
    dir_okay     = False,
    readable     = True,
    resolve_path = True,
)

summaries_file = click.Path(
    exists       = False,
    dir_okay     = False,
    writable     = True,
    resolve_path = True,
)

################################################################################

@click.command()

@click.option(
    "--system",
    type = str,
    required = True,
    help = "Name of docker image."
)

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
    help = "Output path for system generated summaries."
)

@click.option(
    "--keys",
    type = str,
    default = "text",
    help = "List of dataset keys to pass to system. [default = text]"
)

################################################################################

def main(system, dataset, summaries, keys):

    print("Starting", system, "Docker image.")

    process = Popen(

        [
            "docker", "run", "--rm",
            "--name", system,
            "-a", "stdin", "-a", "stdout",
            "-i", system
        ],

        stdin = PIPE,
        stdout = PIPE,

    )

    dataset_file = jsonl.open(dataset, gzip = True)

    # Check the size of the dataset.
    # As a sanity check and for the progress bar.

    print("Loading articles... ", end = "", flush = True)
    dataset_length = len(dataset_file)
    print("found", dataset_length, "articles.\n")

    # Start new thread to feed summaries into container.

    Thread(
        target = _writer,
        args = (process, dataset_file, keys.split(","))
    ).start()

    # Start progress bar.

    progress = tqdm(
        readiter(process.stdout),
        total     = dataset_length,
        desc      = "Running " + system,
    )

    # Prepare to decode summaries.

    is_json = True

    with jsonl.open(summaries, gzip = True) as summaries_file:

        summaries_file.delete()

        with progress as output:
            for line in output:

                summaries_file.appendline({"system": line})

    print("\nRun complete. Next, evaluate with newsroom-score.")

################################################################################
