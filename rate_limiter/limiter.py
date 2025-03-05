from flask import Flask, jsonify
import time

app = Flask(__name__)

bucket_size = 10

def add_token():
    global bucket_size
    time.sleep(1)
    bucket_size += 1

#you create apis in flask by using app routers.
@app.route('/limited', methods = ["GET"])
def limited():
    global bucket_size
    
    return jsonify({"message": "Limited"})

#you create apis in flask by using app routers.
@app.route('/unlimited', methods = ["GET"])
def unlimited():
    return jsonify({"message": "Unlimited!"})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)  # Change 8080 to your desired port
