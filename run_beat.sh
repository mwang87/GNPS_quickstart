#!/bin/bash

celery -A tasks_periodic beat -l info -c 1 -B