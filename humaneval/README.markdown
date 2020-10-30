We used Amazon Mechanical Turk for human evaluation.
Here are the instructions to replicate our process fully.

Worker Qualifications
---------------------

Our only qualification is requiring workers to be from the United States.
However, we also limit participation to Mechanical Turk's "Master Workers."
This is to improve response quality based on pilot studies.
Mechanical Turk charges a premium for this, on top of base payment.
I don't believe this premium is paid to workers, so we don't factor it in to worker payment, below.

Worker Payment
--------------

The base rate per task was $0.45.
All HITs were launched together in one batch manually, all at the same price.
The price was chosen to make sure workers are paid at least US minimum wage (rounded up to $8/hour).
We assumed workers would read at an average reading speed (roughly 200 WPM).
Because articles have varying lengths, we fixed word count at the 75th percentile (roughly 670 words).

```
(670 words) / (200 WPM) * ($8) / (60 min) = $0.447 ≈ $0.45
```

(In practice, workers tend to read a bit faster than this.
So if they're doing multiple tasks, they make some serious money.
More than a Cornell PhD student, that's for sure.)

Input Data
----------

You can use the HTML file in this directory for task layout.
This file can be directly copied into the Mechanical Turk design interface.
(You might have to relabel your input data or HTML variables, though.)

**Task HTML:** https://github.com/lil-lab/newsroom/blob/master/humaneval/eval.html

Here's a download link for the raw data CSV from our original evaluation.
It contains all article texts, system summaries, and each of the raw crowdworker ratings for the text/system pairs.
It may also be helpful for you if you are comparing your work to previous systems.

**Raw Data:** `newsroom-human-eval.csv`

A copy of the all human ratings — there are 60 articles, 7 systems, and 3 ratings by different people for each system for a total of 1,260 rows. Each row is a single rating across the four dimensions from the paper. The columns are:

- System - name of the sumarization system/baseline being rated
- ArticleID - index of the article in the dataset, can be used to group by article
- ArticleText, ArticleTitle, SystemSummary - three inputs the rater sees (HTML encoded for AMT)
- CoherenceRating, FluencyRating, InformativenessRating, RelevanceRating - ratings (1-5)

The raw data CSV has multiple entries per system for each worker.
So, you will need to deduplicate by article ID to use it as a starting point for your task.
Otherwise, this file provides all input data you need to run the task, minus your system summaries.
Article ID will also let you find the original articles in the full data release, if you need to do this.



Contact us at newsroom-summaries@googlegroups.com if you have questions!
