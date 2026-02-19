#!/bin/bash

source activate python313 && celery -A tasks_conversion worker -l info -c 4 --queues=conversion