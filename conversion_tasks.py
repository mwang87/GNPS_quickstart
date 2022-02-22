from celery import Celery
import os
import json
import requests
import errno
import glob
import shutil

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

def convert_all(sessionid, renumber_scans=False):
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

    if renumber_scans:
        print("RENUMBERING IN SERIAL")

        all_converted_files = glob.glob(os.path.join(save_dir, sessionid, "converted", "*.mzML"))
        output_converted_renumbered_folder = os.path.join(save_dir, sessionid, "converted_renumbered")
        try:
            os.mkdir(output_converted_renumbered_folder)
        except:
            print("output_converted_renumbered_folder Exists")

        all_jobs = []
        for filename in all_converted_files:
            output_filename = os.path.join(output_converted_renumbered_folder, os.path.basename(filename))
            worker_job = renumber_mzML_scans_task.delay(filename, output_filename)
            all_jobs.append(worker_job)

        for job in all_jobs:
            while not job.ready():
                sleep(0.5)
        
        # Cleanup
        #shutil.rmtree(output_conversion_folder)
    

    all_converted_files = glob.glob(os.path.join(save_dir, sessionid, "converted", "*.mzML"))

    summary_list = []
    for converted_file in all_converted_files:
        summary_object = {}
        summary_object["filename"] = os.path.basename(converted_file)
        summary_object["summaryfilename"] = os.path.basename(converted_file)

        summary_list.append(summary_object)

    #Zip up the files
    cmd = "cd %s && zip %s -r %s" % (os.path.join(save_dir, sessionid), "converted.zip", "converted")
    os.system(cmd)

    #Schedule Cleanup
    cleanup_task.apply_async( args=[sessionid], countdown=84600)

    return summary_list

# This is mainly for agilent data
@celery_instance.task(time_limit=120)
def renumber_mzML_scans_task(input_mzML, output_mzML):
    scan_current = 1
    previous_ms1_scan = 0

    with MzMLWriter(open(output_mzML, 'wb'), close=True) as out:
        # Add default controlled vocabularies
        out.controlled_vocabularies()
        # Open the run and spectrum list sections
        with out.run(id="my_analysis"):
            #spectrum_count = len(scans) + sum([len(products) for _, products in scans])
            run = pymzml.run.Reader(input_mzML)
            for spectrum in run:
                if spectrum['ms level'] == 1:
                    out.write_spectrum(
                        spectrum.mz, spectrum.i,
                        id="scan={}".format(scan_current), params=[
                            "MS1 Spectrum",
                            {"ms level": 1},
                            {"total ion current": sum(spectrum.i)}
                        ],
                        scan_start_time=spectrum.scan_time_in_minutes())
                    previous_ms1_scan = scan_current
                    scan_current += 1
                elif spectrum["ms level"] == 2:
                    precursor_spectrum = spectrum.selected_precursors[0]
                    precursor_mz = precursor_spectrum["mz"]
                    precursor_intensity = 0
                    precursor_charge = 0

                    try:
                        precursor_charge = precursor_spectrum["charge"]
                        precursor_intensity = precursor_spectrum["i"]
                    except:
                        pass

                    out.write_spectrum(
                        spectrum.mz, spectrum.i,
                        id="scan={}".format(scan_current), params=[
                            "MS1 Spectrum",
                            {"ms level": 2},
                            {"total ion current": sum(spectrum.i)}
                        ],
                        # Include precursor information
                        precursor_information={
                            "mz": precursor_mz,
                            "intensity": precursor_intensity,
                            "charge": precursor_charge,
                            "scan_id": "scan={}".format(previous_ms1_scan),
                            "activation": ["beam-type collisional dissociation", {"collision energy": spectrum["collision energy"]}]
                        },
                        scan_start_time=spectrum.scan_time_in_minutes())

                    scan_current += 1
