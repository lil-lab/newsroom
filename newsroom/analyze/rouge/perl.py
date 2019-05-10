################################################################################

from pyrouge import Rouge155

import functools
from os.path import abspath, dirname, join
import pyrouge, logging, tempfile
from collections import namedtuple
from os import system
import re

pyrouge.utils.log.logging.disable(logging.CRITICAL)

ROUGEResult = namedtuple("ROUGEResult", [
    "precision", "recall", "fscore"
])

# ROUGE already does this tokenization.
# Perform it now to handle encoding issues.
# Scores will remain the same.

depunct = re.compile(r"[^a-z0-9]")

################################################################################

exceptions_script = join(abspath(dirname(__file__)), "exceptions.sh")
system("sh " + exceptions_script)

################################################################################

@functools.lru_cache()
def PERLROUGE(reference, generated, stem):

    rouge_dir = join(
        dirname(abspath(__file__)),
        "ROUGE-1.5.5")

    rouge = pyrouge.Rouge155(rouge_dir)
    rouge._Rouge155__add_config_option = (lambda options:
        [*options, *(["-m"] if stem else []), rouge._config_file])

    rouge.system_dir = tempfile.mkdtemp("-systems")
    rouge.model_dir  = tempfile.mkdtemp("-models")

    with open(join(rouge.system_dir, "1.txt"), "w", encoding = "utf-8") as f:
        f.write(depunct.sub(" ", generated))

    with open(join(rouge.model_dir, "1.txt"), "w", encoding = "utf-8") as f:
        f.write(depunct.sub(" ", reference))

    rouge.system_filename_pattern = "(\d+).txt"
    rouge.model_filename_pattern  = "#ID#.txt"

    try:
        result = rouge.output_to_dict(rouge.convert_and_evaluate())
    except:
        result = {}

    return tuple(result.items())

def ROUGE_N(reference, system, n = 1, stem = False):

    output = dict(PERLROUGE(reference, system, stem))

    return ROUGEResult(
        output.get(f"rouge_{n}_precision", 0),
        output.get(f"rouge_{n}_recall",    0),
        output.get(f"rouge_{n}_f_score",   0)
    )

def ROUGE_L(reference, system, stem = False):

    output = dict(PERLROUGE(reference, system, stem))

    return ROUGEResult(
        output.get("rouge_l_precision", 0),
        output.get("rouge_l_recall",    0),
        output.get("rouge_l_f_score",   0)
    )

################################################################################
