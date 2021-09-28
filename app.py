#!/usr/bin/env python
# encoding: utf-8
from flask import Flask, request, jsonify, render_template
from azure.cosmos import CosmosClient
from json import JSONEncoder
import os

app = Flask(__name__, static_url_path = "/static", static_folder = "static")

url = os.environ.get('ACCOUNT_URI', 'https://hacktest.documents.azure.com:443/')
key = os.environ.get('ACCOUNT_KEY', '')
client = CosmosClient(url, credential=key)
database_name = 'hackjoblist'
database = client.get_database_client(database_name)
container_name = 'joblist'
container = database.get_container_client(container_name)

@app.route('/foldingjob', methods=['GET'])
def query_records():
    id = request.args.get('id')
    if not id:
        # print(json.dumps(item, indent=True))
        return jsonify(container.query_items(
                query='SELECT * FROM r',
                enable_cross_partition_query=True))
    return jsonify(container.query_items(
        query='SELECT * FROM products p WHERE p.productModel = @model',
        parameters=[
            dict(name='@model', value='Model 7')
        ],
        enable_cross_partition_query=True
    ))

# @app.route('/foldingjob', methods=['POST'])
# def create_record():
#     record = json.loads(request.data)
#     foldingjob = FoldingJob(
#         filename=record['filename'],
#         size=record['size'],
#         contents=record['contents'],
#         created_at=record['created_at'])
#     foldingjob.save()
#     return jsonify(foldingjob)

# @app.route('/foldingjob', methods=['PUT'])
# def update_record():
#     record = json.loads(request.data)
#     foldingjob = FoldingJob.objects(id=record['id']).first()
#     if not foldingjob:
#         return jsonify({'error': 'data not found'})
#     else:
#         foldingjob.update(
#             filename=record['filename'],
#             size=record['size'],
#             contents=record['contents'],
#             created_at=record['created_at'])
#     return jsonify(foldingjob)

# @app.route('/foldingjob', methods=['DELETE'])
# def delete_record():
#     record = json.loads(request.data)
#     foldingjob = FoldingJob.objects(id=record['id']).first()
#     if not foldingjob:
#         return jsonify({'error': 'data not found'})
#     else:
#         foldingjob.delete()
#     return jsonify(foldingjob)


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
        f.close()

        # container.upsert_item({
        #         'id': 'item{0}'.format(i),
        #         'productName': 'Widget',
        #         'productModel': 'Model {0}'.format(i)
        #     }
        # )
        
        foldingjobs = [] # FoldingJob.objects()
        return render_template(
            "upload-file.html", 
            msg="Uploaded: {}".format(f.filename),
            job_id="Folding Job ID: {}".format(None), # foldingjob.id),
            file_size="Size: {} bytes".format(size),
            file_contents="Contents: {}".format(str(data, "utf-8")),
            folding_jobs=foldingjobs,
            jobs=foldingjobs,
            len=len(foldingjobs))
        
    foldingjobs = list(container.query_items(
                query='SELECT * FROM r',
                enable_cross_partition_query=True))
    return render_template(
        "upload-file.html", 
        msg="Please choose a file",
        folding_jobs=foldingjobs,
        jobs=foldingjobs,
        len=len(foldingjobs))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000", debug=True) 