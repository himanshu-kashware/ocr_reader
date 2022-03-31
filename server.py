import asyncio
import re

from flask import Flask

from ocr_reader import getDocumentId

UPLOAD_FOLDER = 'C:/uploads'

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

import os
import urllib.request

from flask import Flask, request, redirect, jsonify
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/file-upload', methods=['POST'])
async def upload_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp
    file = request.files['file']
    if file.filename == '':
        resp = jsonify({'message': 'No file selected for uploading'})
        resp.status_code = 400
        return resp
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        result = await get_document_id(f'{UPLOAD_FOLDER}/{filename}')
        if len(result) == 0:
            result = 'Not Detected'

        resp = jsonify({'message': f'File successfully uploaded named {result}'})
        resp.status_code = 201
        os.remove(f'{UPLOAD_FOLDER}/{filename}')
        return resp
    else:
        resp = jsonify({'message': 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'})
        resp.status_code = 400
        return resp


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)


async def get_document_id(path):
    result = getDocumentId(path)
    length = 10
    var = [word for word in result.split() if len(word) == length]
    doc_name = ''
    for tenWord in var:
        if bool(re.search(r'^[a-zA-Z]{5}[0-9]{4}[a-zA-Z]$', re.sub(r'\s+', '', tenWord))):
            doc_name = re.search(r'^[a-zA-Z]{5}[0-9]{4}[a-zA-Z]$', re.sub(r'\s+', '', tenWord)).string
            break
        else:
            doc_name = ''
    print(f'document name {doc_name}')
    return doc_name
