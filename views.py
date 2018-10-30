# views.py
from flask import abort, jsonify, render_template, request, redirect, url_for, make_response
import uuid

from app import app
import os
import glob
import json
import requests
import util
import credentials


@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    return "{}"

@app.route('/', methods=['GET'])
def classicnetworking():
    response = make_response(render_template('classicnetworking.html'))
    response.set_cookie('username', str(uuid.uuid4()))
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
    username = request.cookies.get('username')
    email = request.form["email"]
    if len(email) < 1 or len(email) > 100:
        email = "ccms.web@gmail.com"

    present_folders = util.check_ftp_folders(username)

    if not "G1" in present_folders:
        content = {'status': 'Group 1 files required but not selected'}
        return json.dumps(content), 417

    remote_dir = os.path.join(credentials.USERNAME, username)
    task_id = util.launch_GNPS_workflow(remote_dir, "GNPS Quickstart Molecular Networking Analysis ", credentials.USERNAME, credentials.PASSWORD, present_folders, email)

    content = {'status': 'Success', 'task_id': task_id}
    return json.dumps(content), 200

"""

Feature Based Molecular Networking Portion

"""
@app.route('/featurebasednetworking', methods=['GET'])
def featurebasednetworking():
    response = make_response(render_template('featurebasednetworking.html'))
    response.set_cookie('username', str(uuid.uuid4()))
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
    username = request.cookies.get('username')
    email = request.form["email"]
    networkingpreset = request.form["networkingpreset"]
    featuretool = request.form["featuretool"]
    if len(email) < 1 or len(email) > 100:
        email = "ccms.web@gmail.com"

    present_folders = util.check_ftp_folders(username)

    if not "featurequantification" in present_folders:
        content = {'status': 'featurequantification required but not selected'}
        return json.dumps(present_folders), 417

    if not "featurems2" in present_folders:
        content = {'status': 'featurems2 required but not selected'}
        return json.dumps(present_folders), 417

    remote_dir = os.path.join(credentials.USERNAME, username)
    task_id = util.launch_GNPS_featurenetworking_workflow(remote_dir, "GNPS Quickstart Molecular Networking Analysis ", credentials.USERNAME, credentials.PASSWORD, email, featuretool, present_folders, networkingpreset)

    #Error
    if len(task_id) != 32:
        content = {'status': 'Error'}
        return json.dumps(content), 500

    content = {'status': 'Success', 'task_id': task_id, 'url': "https://gnps.ucsd.edu/ProteoSAFe/status.jsp?task=%s" % (task_id)}
    return json.dumps(content), 200

@app.route('/uploadanalyzefeaturenetworking', methods=['POST'])
def uploadanalyzefeaturenetworking():
    username = str(uuid.uuid4())
    upload_string = util.upload_single_file(request, "featurequantification")

    networkingpreset = "LOWRES"
    if "networkingpreset" in request.form:
        networkingpreset = request.form["networkingpreset"]


    #Performing Data Upload
    util.upload_single_file_push(request.files["featurequantification"], username, "featurequantification")
    util.upload_single_file_push(request.files["featurems2"], username, "featurems2")

    if "samplemetadata" in request.files:
        util.upload_single_file_push(request.files["samplemetadata"], username, "samplemetadata")

    if "additionalpairs" in request.files:
        util.upload_single_file_push(request.files["additionalpairs"], username, "additionalpairs")

    email = request.form["email"]
    featuretool = request.form["featuretool"]
    if len(email) < 1 or len(email) > 100:
        email = "ccms.web@gmail.com"

    present_folders = util.check_ftp_folders(username)

    if not "featurequantification" in present_folders:
        content = {'status': 'featurequantification required but not selected'}
        return json.dumps(present_folders), 417

    if not "featurems2" in present_folders:
        content = {'status': 'featurems2 required but not selected'}
        return json.dumps(present_folders), 417

    remote_dir = os.path.join(credentials.USERNAME, username)
    task_id = util.launch_GNPS_featurenetworking_workflow(remote_dir, "GNPS Quickstart Molecular Networking Analysis ", credentials.USERNAME, credentials.PASSWORD, email, featuretool, present_folders, networkingpreset)

    #Error
    if len(task_id) != 32:
        content = {'status': 'Error'}
        return json.dumps(content), 500

    content = {'status': 'Success', 'task_id': task_id, 'url': "https://gnps.ucsd.edu/ProteoSAFe/status.jsp?task=%s" % (task_id)}
    return json.dumps(content), 200
