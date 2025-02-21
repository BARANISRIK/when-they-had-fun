from flask import Flask, request, render_template, send_file, redirect, url_for, jsonify
import os
import flask
import sys
import json
import requests

app = flask.Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)