#!/bin/bash

gunicorn -w 4 -b 0.0.0.0:5000 --timeout 3600 --keep-alive 3600 main:app
#python main.py
