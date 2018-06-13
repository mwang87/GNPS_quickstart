# views.py
from flask import abort, jsonify, render_template, request, redirect, url_for, make_response
import uuid

from app import app
from werkzeug.utils import secure_filename
import os
import glob
import json
import ftputil
import requests

import credentials

ALLOWED_EXTENSIONS = set(['mgf', 'mzxml', 'mzml'])



@app.route('/', methods=['GET'])
def homepage():
    response = make_response(render_template('dashboard.html'))
    response.set_cookie('username', str(uuid.uuid4()))
    return response

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload-target', methods=['POST'])
def upload():
    #TODO: Check too big files

    username = request.cookies.get('username')

    if 'file' not in request.files:
        return "{}"
    file = request.files['file']
    if file.filename == '':
        return "{}"
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_dir = os.path.join(app.config['UPLOAD_FOLDER'], username)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        file.save(os.path.join(save_dir, filename))
    else:
        print("not allowed")
        return "ERROR"

    return "filename"

def upload_to_gnps(input_filename, folder_for_spectra):
    url = "ccms-ftp01.ucsd.edu"

    with ftputil.FTPHost(url, credentials.USERNAME, credentials.PASSWORD) as ftp_host:
        names = ftp_host.listdir(ftp_host.curdir)
        if not folder_for_spectra in names:
            print("MAKING DIR")
            ftp_host.mkdir(folder_for_spectra)

        ftp_host.chdir(folder_for_spectra)
        ftp_host.upload(input_filename, os.path.basename(input_filename))

@app.route('/analyze', methods=['POST'])
def analyze():
    username = request.cookies.get('username')
    spectra_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)

    files_to_analyze = glob.glob(spectra_folder + "/*")

    if len(files_to_analyze) > 5:
        return ""

    for input_file in files_to_analyze:
        upload_to_gnps(input_file, username)

    remote_dir = os.path.join("quickstart_GNPS", username)
    task_id = launch_GNPS_workflow(remote_dir, "Analyzing Test Data", credentials.USERNAME, credentials.PASSWORD)

    return task_id


def launch_GNPS_workflow(ftp_path, job_description, username, password):
    invokeParameters = {}
    invokeParameters["workflow"] = "METABOLOMICS-SNETS"
    invokeParameters["protocol"] = "None"
    invokeParameters["desc"] = "Qiita Clustering Job " + job_description
    invokeParameters["library_on_server"] = "d.speclibs;"
    invokeParameters["spec_on_server"] = "d." + ftp_path + ";"
    invokeParameters["tolerance.PM_tolerance"] = "2.0"
    invokeParameters["tolerance.Ion_tolerance"] = "0.5"
    invokeParameters["PAIRS_MIN_COSINE"] = "0.70"
    invokeParameters["MIN_MATCHED_PEAKS"] = "6"
    invokeParameters["TOPK"] = "10"
    invokeParameters["CLUSTER_MIN_SIZE"] = "2"
    invokeParameters["RUN_MSCLUSTER"] = "on"
    invokeParameters["MAXIMUM_COMPONENT_SIZE"] = "100"
    invokeParameters["MIN_MATCHED_PEAKS_SEARCH"] = "6"
    invokeParameters["SCORE_THRESHOLD"] = "0.7"
    invokeParameters["ANALOG_SEARCH"] = "0"
    invokeParameters["MAX_SHIFT_MASS"] = "100.0"
    invokeParameters["FILTER_STDDEV_PEAK_datasetsINT"] = "0.0"
    invokeParameters["MIN_PEAK_INT"] = "0.0"
    invokeParameters["FILTER_PRECURSOR_WINDOW"] = "1"
    invokeParameters["FILTER_LIBRARY"] = "1"
    invokeParameters["WINDOW_FILTER"] = "1"
    invokeParameters["CREATE_CLUSTER_BUCKETS"] = "1"
    invokeParameters["CREATE_ILI_OUTPUT"] = "0"
    invokeParameters["email"] = "mwang87@gmail.com"
    invokeParameters["uuid"] = "1DCE40F7-1211-0001-979D-15DAB2D0B500"

    task_id = invoke_workflow("gnps.ucsd.edu", invokeParameters, username, password)

    return task_id

def invoke_workflow(base_url, parameters, login, password):
    username = login
    password = password

    s = requests.Session()

    payload = {
        'user' : username,
        'password' : password,
        'login' : 'Sign in'
    }

    r = s.post('https://' + base_url + '/ProteoSAFe/user/login.jsp', data=payload, verify=False)
    r = s.post('https://' + base_url + '/ProteoSAFe/InvokeTools', data=parameters, verify=False)
    task_id = r.text

    if len(task_id) > 4 and len(task_id) < 60:
        print("Launched Task: : " + r.text)
        return task_id
    else:
        print(task_id)
        return None
