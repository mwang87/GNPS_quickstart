from celery import Celery
import os
import json
import requests
import errno
import glob
import shutil
import uuid

try:
    from psims.mzml.writer import MzMLWriter
    import pymzml
except:
    pass

from joblib import Parallel, delayed
from werkzeug.utils import secure_filename

import multiprocessing
import subprocess
from time import sleep


celery_instance = Celery('tasks_conversion', backend='redis://gnpsquickstart-redis', broker='redis://gnpsquickstart-redis')

@celery_instance.task(time_limit=180)
def test_up():
    return "Up"