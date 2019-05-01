#!/bin/sh

cd ROUGE-1.5.5/data/WordNet-2.0-Exceptions/
./buildExeptionDB.pl . exc WordNet-2.0.exc.db > /dev/null

cd ..
rm WordNet-2.0.exc.db
ln -s WordNet-2.0-Exceptions/WordNet-2.0.exc.db
