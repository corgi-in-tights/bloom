#!/bin/bash

# export env
export $(grep -v '^#' .env | xargs)

python app/index.py