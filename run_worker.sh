#!/bin/bash

celery -A conversion_tasks worker -l info -c 4