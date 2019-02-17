from flask import Flask, jsonify
from flask_cors import cross_origin

app = Flask(__name__)


@app.route('/')
@cross_origin()
def hello_world():
    return jsonify('Noteify FTW!')


if __name__ == '__main__':
    app.run()
