from flask import Flask, request, jsonify
# from cpu import CPU
from ls8 import ls8
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hit up the ls8 endpoint wid a POST'


@app.route('/ls8', methods=['POST'])
def main():
    data = request.get_json()
    description = data['description'][41:]

    f = open("room.ls8", "w")
    f.write(description)
    f.close()

    room_id = ls8()

    response = {
        "room": room_id[-3:]
    }

    return jsonify(response), 200

if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000, debug=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
