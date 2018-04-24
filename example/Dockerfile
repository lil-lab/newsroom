FROM continuumio/miniconda3

RUN pip install gensim
COPY . .

ENTRYPOINT python textrank.py
