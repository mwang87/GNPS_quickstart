# views.py
from flask import abort, jsonify, render_template, request, redirect, url_for, make_response, send_from_directory
import uuid

from app import app
import os
import glob
import json
import requests
import util
import util_spectrumannotation
import credentials
import urllib.parse

@app.route('/validatebatch', methods=['GET'])
def validatebatch():
    return render_template('validatebatch.html')
