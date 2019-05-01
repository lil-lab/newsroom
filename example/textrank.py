import json, sys

from gensim.summarization.summarizer import summarize


WORD_COUNT = 50

for line in sys.stdin:

    article = json.loads(line)

    try:

        summary = summarize(
            article["text"],
            word_count = WORD_COUNT)

    except ValueError:

        # Handles "input must have more than one sentence"

        summary = article["text"]

    print(summary.replace("\n", " "), flush = True)
