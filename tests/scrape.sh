#!/bin/sh

cd `dirname $0`
newsroom-scrape --urls urls.txt --archive tests.archive
