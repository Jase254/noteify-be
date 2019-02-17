from flask import Flask, jsonify
from flask_cors import cross_origin
from HumongousDB import HumongousDB
from ExquisiteSushi import ExquisiteSushi
from text_extraction import downloadFullBucket
from google.cloud import storage

app = Flask(__name__)


@app.route('/')
@cross_origin()
def allImages():
    storage_client = storage.Client("noteify")
    bucket = storage_client.get_bucket("noteify")

    local_storage = ExquisiteSushi()
    local_storage2 = ExquisiteSushi()

    database = HumongousDB()
    database.init_connection()
    database.init_database("Noteify")
    database.init_collection("Images")

    database2 = HumongousDB()
    database2.init_connection()
    database2.init_database("Noteify2")
    database2.init_collection("Tags")

    downloadFullBucket(database, database2, bucket)

    data = database2.getDatabase()
    print(data)


    return jsonify(data)

@app.route('/test')
@cross_origin()
def test():
    x=dict()
    x['http://ec2-54-193-114-159.us-west-1.compute.amazonaws.com:5000/static/img-16-02-22_46_00.jpg']=['mango','django','stuff']
    return jsonify(x)


if __name__ == '__main__':
    app.run(host="0.0.0.0")
   # app.run()
