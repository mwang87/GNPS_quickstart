# views.py
from flask import abort, jsonify, render_template, request, redirect, url_for, make_response, send_from_directory
import uuid

from app import app
import os
import glob
import json
import urllib.parse
import pandas as pd
import batch_validator

def allowed_file_metadata(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ["tsv"]

@app.route('/validatebatch', methods=['GET'])
def validatebatch():
    return render_template('validatebatch.html')


@app.route('/validatebatch', methods=['POST'])
def validatebatchpost():
    request_file = request.files['file']
    #Invalid File Types
    if not allowed_file_metadata(request_file.filename):
        error_dict = {}
        error_dict["header"] = "Incorrect File Type"
        error_dict["line_number"] = "N/A"
        error_dict["error_string"] = "Please provide a tab separated file"

        validation_dict = {}
        validation_dict["status"] = False
        validation_dict["errors"] = [error_dict]
        validation_dict["stats"] = []
        validation_dict["stats"].append({"type":"total_rows", "value": 0})
        validation_dict["stats"].append({"type":"valid_rows", "value": 0})

        return json.dumps(validation_dict)
    
    
    local_filename = os.path.join(app.config['UPLOAD_FOLDER'], str(uuid.uuid4()))
    request_file.save(local_filename)
     
    """Trying stuff out with pandas"""
    metadata_df = pd.read_csv(local_filename, keep_default_na=False, sep="\t")
    metadata_df = metadata_df.truncate(after=2000)
    metadata_df.to_csv(local_filename, index=False, sep="\t")
    
    pass_validation, failures, errors_list, valid_rows, total_rows = batch_validator.perform_batch_validation(local_filename)

    validation_dict = {}
    validation_dict["status"] = pass_validation
    validation_dict["errors"] = errors_list
    validation_dict["stats"] = []

    validation_dict["stats"].append({"type":"total_rows", "value":total_rows})
    validation_dict["stats"].append({"type":"valid_rows", "value":len(valid_rows)})

    return json.dumps(validation_dict)