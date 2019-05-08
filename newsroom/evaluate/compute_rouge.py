from newsroom.analyze.rouge import ROUGE_N, ROUGE_L

def compute_rouge(info):

    aline, sline, rouges, stemmed = info
    scores = {}

    ref = aline["summary"]
    sys = sline["system"]

    for rouge in rouges:

        if rouge == "L":

            result = ROUGE_L(ref, sys, stem = stemmed)

        else:

            result = ROUGE_N(ref, sys, n = int(rouge), stem = stemmed)

        for kind in ("precision", "recall", "fscore"):

            scores[f"rouge_{rouge}_{kind}"] = getattr(result, kind)

    scores["reference"] = ref
    scores["system"] = sys

    scores.update({
        k: v for k, v in aline.items()
        if k not in ("text", "summary", "title")
    })
    
    return scores

