from flask import Flask, jsonify


app = Flask(__name__)

@app.route("/health",methods = ["GET"])
def health():
    return jsonify({"message": "I'm alive"}), 200

@app.route("/",methods = ["GET"])
def server():
    return jsonify({"message": "From Server 2"}), 200

###############################################################

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9091, debug=True)  
    
