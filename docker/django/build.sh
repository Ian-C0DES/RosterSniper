#!/bin/bash

# https://stackoverflow.com/a/3355423
cd "$(dirname "$0")"

docker build -f Dockerfile ../.. -t rs_django --squash
