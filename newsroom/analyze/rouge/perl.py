################################################################################

from pyrouge import Rouge155

import functools
from os.path import abspath, dirname, join
import pyrouge, logging, tempfile
from collections import namedtuple
from os import system

pyrouge.utils.log.logging.disable(logging.CRITICAL)

ROUGEResult = namedtuple("ROUGEResult", [
    "precision", "recall", "fscore"
])

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
        f.write(generated)

    with open(join(rouge.model_dir, "1.txt"), "w", encoding = "utf-8") as f:
        f.write(reference)

    rouge.system_filename_pattern = "(\d+).txt"
    rouge.model_filename_pattern  = "#ID#.txt"

    result = rouge.output_to_dict(rouge.convert_and_evaluate())

    return tuple(result.items())

def ROUGE_N(reference, system, n = 1, stem = False):

    output = dict(PERLROUGE(reference, system, stem))

    return ROUGEResult(
        output[f"rouge_{n}_precision"],
        output[f"rouge_{n}_recall"],
        output[f"rouge_{n}_f_score"]
    )

def ROUGE_L(reference, system, stem = False):

    output = dict(PERLROUGE(reference, system, stem))

    return ROUGEResult(
        output["rouge_l_precision"],
        output["rouge_l_recall"],
        output["rouge_l_f_score"]
    )

################################################################################
