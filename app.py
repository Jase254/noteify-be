from flask import Flask, jsonify
from flask_cors import cross_origin

app = Flask(__name__)


@app.route('/')
@cross_origin()
def hello_world():
    return jsonify('Noteify FTW!')

@app.route('/test')
@cross_origin()
def test():
    x=dict()
    x['http://ec2-54-193-114-159.us-west-1.compute.amazonaws.com:5000/static/img-16-02-22_46_00.jpg']=['mango','django','stuff']
    return jsonify(x)


if __name__ == '__main__':
    app.run(host="0.0.0.0")
