# views.py
from flask import abort, jsonify, render_template, request, redirect, url_for, make_response
import uuid

from app import app
import os
import glob
import json
import requests
import util
import util_spectrumannotation
import credentials


@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    return "{}"

@app.route('/', methods=['GET'])
def classicnetworking():
    response = make_response(render_template('classicnetworking.html'))
    response.set_cookie('sessionid', str(uuid.uuid4()))
    response.set_cookie('selectedFiles', "False")

    return response

@app.route('/upload1', methods=['POST'])
def upload_1():
    upload_string = util.upload_single_file(request, "G1")
    response = make_response()
    response.set_cookie('selectedFiles', "True")

    return response

@app.route('/upload2', methods=['POST'])
def upload_2():
    upload_string = util.upload_single_file(request, "G2")
    response = make_response()
    response.set_cookie('selectedFiles', "True")

    return response

@app.route('/upload3', methods=['POST'])
def upload_3():
    upload_string = util.upload_single_file(request, "G3")
    response = make_response()
    response.set_cookie('selectedFiles', "True")

    return response

@app.route('/analyze', methods=['POST'])
def analyze():
    sessionid = request.cookies.get('sessionid')
    networkingpreset = request.form["networkingpreset"]
    email = request.form["email"]
    if len(email) < 1 or len(email) > 100:
        email = "ccms.web@gmail.com"

    present_folders = util.check_ftp_folders(sessionid)

    if not "G1" in present_folders:
        content = {'status': 'Group 1 files required but not selected'}
        return json.dumps(content), 417

    gnps_username = credentials.USERNAME
    gnps_password = credentials.PASSWORD

    try:
        if len(request.form["username"] ) > 3 and len(request.form["password"]):
            gnps_username = request.form["username"]
            gnps_password = request.form["password"]
    except:
        gnps_username = credentials.USERNAME
        gnps_password = credentials.PASSWORD

    remote_dir = os.path.join(credentials.USERNAME, sessionid)
    task_id = util.launch_GNPS_workflow(remote_dir, "GNPS Quickstart Molecular Networking Analysis ", gnps_username, gnps_password, present_folders, email, networkingpreset)

    content = {'status': 'Success', 'task_id': task_id}
    return json.dumps(content), 200

"""

Feature Based Molecular Networking Portion

"""
@app.route('/featurebasednetworking', methods=['GET'])
def featurebasednetworking():
    response = make_response(render_template('featurebasednetworking.html'))
    response.set_cookie('sessionid', str(uuid.uuid4()))
    response.set_cookie('featurequantification', "False")
    response.set_cookie('featurems2', "False")
    response.set_cookie('samplemetadata', "False")
    response.set_cookie('additionalpairs', "False")

    return response

@app.route('/featurequantification', methods=['POST'])
def featurequantification():
    upload_string = util.upload_single_file(request, "featurequantification")
    response = make_response()
    response.set_cookie('featurequantification', "True")

    return response

@app.route('/featurems2', methods=['POST'])
def featurems2():
    upload_string = util.upload_single_file(request, "featurems2")
    response = make_response()
    response.set_cookie('featurems2', "True")

    return response

@app.route('/samplemetadata', methods=['POST'])
def samplemetadata():
    upload_string = util.upload_single_file(request, "samplemetadata")
    response = make_response()
    response.set_cookie('samplemetadata', "True")

    return response

@app.route('/additionalpairs', methods=['POST'])
def additionalpairs():
    upload_string = util.upload_single_file(request, "additionalpairs")
    response = make_response()
    response.set_cookie('additionalpairs', "True")

    return response

@app.route('/analyzefeaturenetworking', methods=['POST'])
def analyzefeaturenetworking():
    sessionid = request.cookies.get('sessionid')

    print(sessionid)

    email = request.form["email"]
    networkingpreset = request.form["networkingpreset"]
    featuretool = request.form["featuretool"]
    if len(email) < 1 or len(email) > 100:
        email = "ccms.web@gmail.com"

    present_folders = util.check_ftp_folders(sessionid)

    if not "featurequantification" in present_folders:
        content = {'status': 'featurequantification required but not selected'}
        return json.dumps(present_folders), 417

    if not "featurems2" in present_folders:
        content = {'status': 'featurems2 required but not selected'}
        return json.dumps(present_folders), 417


    gnps_username = credentials.USERNAME
    gnps_password = credentials.PASSWORD

    try:
        if len(request.form["username"] ) > 3 and len(request.form["password"]):
            gnps_username = request.form["username"]
            gnps_password = request.form["password"]
    except:
        gnps_username = credentials.USERNAME
        gnps_password = credentials.PASSWORD

    remote_dir = os.path.join(credentials.USERNAME, sessionid)
    task_id = util.launch_GNPS_featurenetworking_workflow(remote_dir, "GNPS Quickstart Molecular Networking Analysis ", gnps_username, gnps_password, email, featuretool, present_folders, networkingpreset)

    #Error
    if len(task_id) != 32:
        content = {'status': 'Error'}
        return json.dumps(content), 500

    content = {'status': 'Success', 'task_id': task_id, 'url': "https://gnps.ucsd.edu/ProteoSAFe/status.jsp?task=%s" % (task_id)}
    return json.dumps(content), 200


"""This is a single shot upload and submit API endpoint built for Robin's module in MZMine2"""
@app.route('/uploadanalyzefeaturenetworking', methods=['POST'])
def uploadanalyzefeaturenetworking():
    sessionid = str(uuid.uuid4())
    upload_string = util.upload_single_file(request, "featurequantification")

    networkingpreset = "LOWRES"
    if "networkingpreset" in request.form:
        networkingpreset = request.form["networkingpreset"]


    #Performing Data Upload
    util.upload_single_file_push(request.files["featurequantification"], sessionid, "featurequantification")
    util.upload_single_file_push(request.files["featurems2"], sessionid, "featurems2")

    if "samplemetadata" in request.files:
        util.upload_single_file_push(request.files["samplemetadata"], sessionid, "samplemetadata")

    if "additionalpairs" in request.files:
        util.upload_single_file_push(request.files["additionalpairs"], sessionid, "additionalpairs")

    email = ""
    try:
        email = request.form["email"]
    except:
        email = ""
    if len(email) < 1 or len(email) > 100:
        email = "ccms.web@gmail.com"

    featuretool = request.form["featuretool"]
    present_folders = util.check_ftp_folders(sessionid)

    if not "featurequantification" in present_folders:
        content = {'status': 'featurequantification required but not selected'}
        return json.dumps(present_folders), 417

    if not "featurems2" in present_folders:
        content = {'status': 'featurems2 required but not selected'}
        return json.dumps(present_folders), 417

    gnps_username = credentials.USERNAME
    gnps_password = credentials.PASSWORD

    try:
        if len(request.form["username"] ) > 3 and len(request.form["password"]):
            gnps_username = request.form["username"]
            gnps_password = request.form["password"]
    except:
        gnps_username = credentials.USERNAME
        gnps_password = credentials.PASSWORD

    task_description = "GNPS Quickstart Molecular Networking Analysis from MZmine2"

    if "description" in request.form:
        if len(request.form["description"]) > 1:
            task_description = request.form["description"]

    remote_dir = os.path.join(credentials.USERNAME, sessionid)
    task_id = util.launch_GNPS_featurenetworking_workflow(remote_dir, task_description, gnps_username, gnps_password, email, featuretool, present_folders, networkingpreset)

    #Error
    if len(task_id) != 32:
        content = {'status': 'Error'}
        return json.dumps(content), 500

    content = {'status': 'Success', 'task_id': task_id, 'url': "https://gnps.ucsd.edu/ProteoSAFe/status.jsp?task=%s" % (task_id)}
    return json.dumps(content), 200


"""This is a single shot upload and submit API endpoint built to add reference MS/MS spectra"""
@app.route('/depostsinglespectrum', methods=['POST'])
def depositsinglespectrum():
    gnps_username = request.form["username"]
    gnps_password = request.form["password"]

    """Debugging"""
    TEST = False
    if "test" in request.form:
        gnps_username = credentials.USERNAME
        gnps_password = credentials.PASSWORD
        TEST = True

    email = ""
    try:
        email = request.form["email"]
    except:
        email = ""
    if len(email) < 1 or len(email) > 100:
        email = "ccms.web@gmail.com"

    print("SPECTRUM STRING", request.form["spectrum"])

    reference_spectrum = json.loads(request.form["spectrum"])

    """Saving Spectrum"""
    save_filename = os.path.join(app.config['UPLOAD_FOLDER'], "reference_spectra", str(uuid.uuid4()) + ".mgf")
    util_spectrumannotation.save_spectrum(reference_spectrum, save_filename)
    util.upload_to_gnps(save_filename, "reference_spectra", "reference_spectra", username=gnps_username, password=gnps_password)

    """Submitting Spectrum"""
    task = util_spectrumannotation.launch_addreferencespectrum_workflow(reference_spectrum, save_filename, "f." + os.path.join(gnps_username, "reference_spectra", "reference_spectra", os.path.basename(save_filename)), gnps_username, gnps_password, email, test=TEST)

    return task
