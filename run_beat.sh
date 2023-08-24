#!/bin/bash

celery -A tasks_periodic worker -l info -c 1 -B --queues=beat