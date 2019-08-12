from celery import Celery
import os
import json
import requests
import errno
from werkzeug.utils import secure_filename
import glob

from joblib import Parallel, delayed
import multiprocessing
import subprocess
from time import sleep
import shutil

celery_instance = Celery('conversion_tasks', backend='redis://gnpsquickstart-redis', broker='redis://gnpsquickstart-redis')

@celery_instance.task(time_limit=120)
def run_shell_command(script_to_run):
    try:
        os.system(script_to_run)
    except KeyboardInterrupt:
        raise
    except:
        return "FAILURE"
    return "DONE"

def run_shell_command_timeout(parameter_dict):
    p = None
    try:
        print(parameter_dict["command"])
        p = subprocess.Popen(parameter_dict["command"])
        p.wait(parameter_dict["timeout"])
    except subprocess.TimeoutExpired:
        p.kill()
        return "FAILURE"
    except KeyboardInterrupt:
        raise
    except:
        return "FAILURE"
    return "DONE"

#Wraps running in parallel a set of shell scripts
def run_parallel_shellcommands(input_shell_commands, parallelism_level, timeout=None):
    if timeout != None:
        parameters_list = []
        for command in input_shell_commands:
            parameter_object = {}
            parameter_object["command"] = command
            parameter_object["timeout"] = timeout
            parameters_list.append(parameter_object)
        return run_parallel_job(run_shell_command_timeout, parameters_list, parallelism_level)
    else:
        return run_parallel_job(run_shell_command, input_shell_commands, parallelism_level)

#Wraps the parallel job running, simplifying code
def run_parallel_job(input_function, input_parameters_list, parallelism_level):
    if parallelism_level == 1:
        output_results_list = []
        for input_param in input_parameters_list:
            result_object = input_function(input_param)
            output_results_list.append(result_object)

        return output_results_list
    else:
        results = Parallel(n_jobs = parallelism_level)(delayed(input_function)(input_object) for input_object in input_parameters_list)
        return results

ALLOWED_EXTENSIONS = set(['mgf', 'mzxml', 'mzml', 'csv', 'txt', "raw"])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_single_file(request):
    sessionid = request.cookies.get('sessionid')
    request_file = request.files['file']

    filename = ""

    save_dir = "/output"
    if "fullPath" in request.form:
        local_filename = os.path.join(save_dir, sessionid, "input", request.form["fullPath"])
    else:
        filename = secure_filename(request_file.filename)
        local_filename = os.path.join(save_dir, sessionid, "input", filename)

    if 'file' not in request.files:
        return "{}"

    if not os.path.exists(os.path.dirname(local_filename)):
        try:
            os.makedirs(os.path.dirname(local_filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


    request_file.save(local_filename)

    print(request_file.filename)

@celery_instance.task(time_limit=120)
def summarize_file(input_filename, output_html):
    cmd = "Rscript mzscript.R %s %s" % (input_filename, output_html)
    print(cmd)
    os.system(cmd)

@celery_instance.task()
def cleanup_task(sessionid):
    save_dir = "/output"
    remove_path = os.path.join(save_dir, sessionid, "*")
    all_paths_to_remove = glob.glob(remove_path)
    for path_to_remove in all_paths_to_remove:
        print("Removing", path_to_remove)
        if os.path.isdir(path_to_remove):
            shutil.rmtree(path_to_remove)
        else:
            os.remove(path_to_remove)

def convert_all(sessionid):
    save_dir = "/output"
    output_conversion_folder = os.path.join(save_dir, sessionid, "converted")
    output_summary_folder = os.path.join(save_dir, sessionid, "summary")

    try:
        os.mkdir(output_summary_folder)
    except:
        print("Summary Folder Exists")

    all_bruker_files = glob.glob(os.path.join(save_dir, sessionid, "input", "*.d"))
    all_thermo_files = glob.glob(os.path.join(save_dir, sessionid, "input", "*.raw"))
    all_thermo_files += glob.glob(os.path.join(save_dir, sessionid, "input", "*.RAW"))
    all_sciex_files = glob.glob(os.path.join(save_dir, sessionid, "input", "*.wiff"))
    all_mzXML_files = glob.glob(os.path.join(save_dir, sessionid, "input", "*.mzXML"))
    all_mzML_files = glob.glob(os.path.join(save_dir, sessionid, "input", "*.mzML"))

    conversion_commands = []

    """Bruker Conversion"""
    for filename in all_bruker_files:
        output_filename = os.path.basename(filename).replace(".d", ".mzML")
        cmd = 'wine msconvert %s --32 --zlib --ignoreUnknownInstrumentError --filter "peakPicking true 1-" --outdir %s --outfile %s' % (filename, output_conversion_folder, output_filename)
        conversion_commands.append(cmd)

    """Thermo Conversion"""
    for filename in all_thermo_files:
        output_filename = os.path.basename(filename).replace(".raw", ".mzML")
        cmd = 'wine msconvert %s --32 --zlib --ignoreUnknownInstrumentError --filter "peakPicking true 1-" --outdir %s --outfile %s' % (filename, output_conversion_folder, output_filename)
        conversion_commands.append(cmd)

    """Sciex Conversion"""
    for filename in all_sciex_files:
        output_filename = os.path.basename(filename).replace(".wiff", ".mzML")
        cmd = 'wine msconvert %s --32 --zlib --ignoreUnknownInstrumentError --filter "peakPicking true 1-" --outdir %s --outfile %s' % (filename, output_conversion_folder, output_filename)
        conversion_commands.append(cmd)

    """mzXML/mzML Conversion"""
    for filename in all_mzXML_files + all_mzML_files:
        output_filename = os.path.basename(filename).replace(".mzXML", ".mzML")
        cmd = 'wine msconvert %s --32 --zlib --ignoreUnknownInstrumentError --filter "peakPicking true 1-" --outdir %s --outfile %s' % (filename, output_conversion_folder, output_filename)
        conversion_commands.append(cmd)

    """Converting in Parallel"""
    #run_parallel_shellcommands(conversion_commands, 32)
    all_jobs = []
    for command in conversion_commands:
        worker_job = run_shell_command.delay(command)
        all_jobs.append(worker_job)

    for job in all_jobs:
        while not job.ready():
            sleep(0.5)

    all_converted_files = glob.glob(os.path.join(save_dir, sessionid, "converted", "*.mzML"))

    #Create Summary For Files
    for filename in all_converted_files:
        html_filename = os.path.join(output_summary_folder, os.path.basename(filename) + ".html")
        summarize_file.delay(filename, html_filename)

    summary_list = []
    for converted_file in all_converted_files:
        summary_object = {}
        summary_object["filename"] = os.path.basename(converted_file)
        summary_object["summaryurl"] = "/summary?filename=%s" % (os.path.basename(converted_file))

        summary_list.append(summary_object)

    #Tar up the files
    cmd = "cd %s && tar -cvf %s %s" % (os.path.join(save_dir, sessionid), "converted.tar", "converted")
    os.system(cmd)

    #Schedule Cleanup
    cleanup_task.apply_async( args=[sessionid], countdown=84600)

    return summary_list

