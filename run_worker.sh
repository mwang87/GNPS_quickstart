#!/bin/bash

celery -A tasks_conversion worker -l info -c 4 --queues=conversion