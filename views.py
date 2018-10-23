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
import util
import credentials


@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    return "{}"

@app.route('/', methods=['GET'])
def homepage():
    response = make_response(render_template('dashboard.html'))
    response.set_cookie('username', str(uuid.uuid4()))
    response.set_cookie('selectedFiles', "False")

    return response

@app.route('/upload1', methods=['POST'])
def upload_1():
    upload_string = util.upload_single_file(request, "G1")
    response = make_response(render_template('dashboard.html'))
    response.set_cookie('selectedFiles', "True")

    return response

@app.route('/upload2', methods=['POST'])
def upload_2():
    upload_string = util.upload_single_file(request, "G2")
    response = make_response(render_template('dashboard.html'))
    response.set_cookie('selectedFiles', "True")

    return response

@app.route('/upload3', methods=['POST'])
def upload_3():
    upload_string = util.upload_single_file(request, "G3")
    response = make_response(render_template('dashboard.html'))
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

    spectra_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)

    remote_dir = os.path.join("quickstart_GNPS", username)
    task_id = util.launch_GNPS_workflow(remote_dir, "GNPS Quickstart Molecular Networking Analysis ", credentials.USERNAME, credentials.PASSWORD, present_folders, email)

    content = {'status': 'Success', 'task_id': task_id}
    return json.dumps(content), 200
