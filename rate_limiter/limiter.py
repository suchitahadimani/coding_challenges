from flask import Flask

app = Flask(__name__)

#you create apis in flask by using app routers.
@app.route('/limited', methods = ["GET"])
def limited():
    return "limited"

#you create apis in flask by using app routers.
@app.route('/limited', methods = ["GET"])
def limited():
    return "limited"