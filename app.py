#!/usr/bin/env python
# encoding: utf-8
from bson import json_util
from flask import Flask, request, jsonify, render_template
from flask_mongoengine import MongoEngine
from datetime import datetime
import json
from json import JSONEncoder
import os
import ssl

app = Flask(__name__, static_url_path = "/static", static_folder = "static")

app.config['MONGODB_SETTINGS'] = {
    'db': 'testusers',
    'host': 'hack2021mongodb.mongo.cosmos.azure.com',
    'port': 10255,
    'username': 'hack2021mongodb',
    'password': 'niOxJthXVqa5Scy6gjeRnd2LZ1WVPGpoqKzW728zyWt7huHloTj7Ndqo1gia0zRVxTkz5gHLeOXz7eq8Osb9lg==',
    'authentication_source': 'admin',
    'authentication_mechanism': 'SCRAM-SHA-1',
    'ssl': True,
    'ssl_cert_reqs': ssl.CERT_NONE,
    'retrywrites': False
}
db = MongoEngine()
db.init_app(app)

def parse_json(data):
    return json.loads(json_util.dumps(data))

class FoldingJob(db.Document):
    filename = db.StringField()
    size = db.IntField()
    contents = db.StringField()
    created_at = db.DateTimeField()
    def to_json(self):
        return {"id": self.id,
                "filename": self.filename,
                "size": self.size,
                "contents": self.contents,
                "created_at": self.created_at}

@app.route('/foldingjob', methods=['GET'])
def query_records():
    id = request.args.get('id')
    foldingjob = FoldingJob.objects(id=id).first()
    if not foldingjob:
        return jsonify({'error': 'data not found'})
    else:
        return jsonify(foldingjob)

@app.route('/foldingjob', methods=['POST'])
def create_record():
    record = json.loads(request.data)
    foldingjob = FoldingJob(
        filename=record['filename'],
        size=record['size'],
        contents=record['contents'],
        created_at=record['created_at'])
    foldingjob.save()
    return jsonify(foldingjob)

@app.route('/foldingjob', methods=['PUT'])
def update_record():
    record = json.loads(request.data)
    foldingjob = FoldingJob.objects(id=record['id']).first()
    if not foldingjob:
        return jsonify({'error': 'data not found'})
    else:
        foldingjob.update(
            filename=record['filename'],
            size=record['size'],
            contents=record['contents'],
            created_at=record['created_at'])
    return jsonify(foldingjob)

@app.route('/foldingjob', methods=['DELETE'])
def delete_record():
    record = json.loads(request.data)
    foldingjob = FoldingJob.objects(id=record['id']).first()
    if not foldingjob:
        return jsonify({'error': 'data not found'})
    else:
        foldingjob.delete()
    return jsonify(foldingjob)


# subclass JSONEncoder
class FoldingJobEncoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == 'POST':
        f = request.files['file_name']
        # read first line
        data = f.readline()
        # get the cursor positioned at end
        f.seek(0, os.SEEK_END)
        # this will be equivalent to size of file
        size = f.tell()
        print("Size of file is ************:", size, "bytes")
        f.close()
        foldingjob = FoldingJob(
            filename=f.filename,
            size=size,
            contents=data,
            created_at=datetime.now())
        foldingjob.save()
        
        foldingjobs = FoldingJob.objects()
        return render_template(
            "upload-file.html", 
            msg="Uploaded: {}".format(f.filename),
            job_id="Folding Job ID: {}".format(foldingjob.id),
            file_size="Size: {} bytes".format(size),
            file_contents="Contents: {}".format(str(data, "utf-8")),
            folding_jobs=foldingjobs.to_json(),
            jobs=foldingjobs,
            len=len(foldingjobs))
        
    foldingjobs = FoldingJob.objects()
    return render_template(
        "upload-file.html", 
        msg="Please choose a file",
        folding_jobs=foldingjobs.to_json(),
        jobs=foldingjobs,
        len=len(foldingjobs))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000", debug=True) 