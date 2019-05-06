from newsroom import jsonl
from gensim.summarization.summarizer import summarize


WORD_COUNT = 50

with jsonl.open("input.dataset", gzip = True) as inputs:
    with jsonl.open("textrank.summaries", gzip = True) as outputs:
        
        outputs.delete()
    
        for article in data:

            try:

                summary = summarize(
                    article["text"],
                    word_count = WORD_COUNT)

            except ValueError:

                # Handles "input must have more than one sentence"

                summary = article["text"]

            outputs.appendline({"system": summary.replace("\n", " ")})
