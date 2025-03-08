from flask import Flask, jsonify
import time
import threading
from math import floor

app = Flask(__name__)
lock = threading.Lock()


############################################################### TOKEN_BUCKET
bucket_size = 10

#10 reqs/s

def add_token():
    global bucket_size

    while True:
        time.sleep(1)
        with lock:
            if bucket_size < 10:
                bucket_size += 1
    

#you create apis in flask by using app routers.
@app.route('/token_bucket', methods = ["GET"])
def token_bucket():
    global bucket_size
    with lock:
        if (bucket_size):
            bucket_size -= 1
            return jsonify({"message": "Request completed"}), 200
    
    return jsonify({"message": "Too many requests, cannot track"}), 429


############################################################### LEAKY BUCKET


tokens = 10
#10 reqs/s

def remove_token():
    global tokens

    while True:
        time.sleep(1)
        with lock:
            if tokens > 0:
                tokens -= 1
    
@app.route('/leaky_bucket', methods = ["GET"])
def leaky_bucket():
    global tokens
    with lock:
        if (tokens < 10):
            tokens += 1
            return jsonify({"message": "Request completed"}), 200
    
    return jsonify({"message": "Too many requests, cannot track"}), 429


############################################################### FIXED WINDOW

window = 10
#10 reqs/s

def reset_window():
    global window
    while True:
        time.sleep(1)
        with lock:
            window = 10

@app.route('/window_counter', methods = ["GET"])
def window_counter():
    global window
    with lock:
        if (window):
            window -= 1
            return jsonify({"message": "Request completed"}), 200
    
    return jsonify({"message": "Too many requests, cannot track"}), 429


############################################################### SLIDING WINDOW LOG

log = []

def window_log():
    global log
    while True:
        with lock:
            if(log and (time.time() - log[0]) > 1):
                log.pop(0)

@app.route('/sliding_window_log', methods = ["GET"])
def sliding_window_log():
    global log
    with lock:
        current_ts = time.time()
        n = len(log)
        if(n < 15): 
            log.append(current_ts)   
            return jsonify({"message": f"Current log : {n}"}), 200
    
    return jsonify({"message": "Too many requests, cannot track"}), 429


############################################################### SLIDING WINDOW COUNTER

prev_window = 0
curr_window = 0

#20 reqs/s

def window_counter():
    global prev_window
    global curr_window
    while True:
        time.sleep(0.5)
        with lock:
            prev_window = curr_window
            curr_window = 0

@app.route('/sliding_window_counter', methods = ["GET"])
def sliding_window_counter():
    global prev_window
    global curr_window
    with lock:
        current_time = time.time() % 30
        time_factor = current_time / 30
        estimated_requests = prev_window * (1 - time_factor) + curr_window
        if (floor(estimated_requests) < 10):
            curr_window += 1
            return jsonify({"message": f" Success --- Estimated Reqs: {floor(estimated_requests)}"}), 200
    
    return jsonify({"message": f"Too many requests, cannot track"}), 429


###############################################################

if __name__ == '__main__':
    threading.Thread(target=reset_window, daemon=True).start() 
    threading.Thread(target=add_token, daemon=True).start() 
    threading.Thread(target=remove_token, daemon=True).start()
    threading.Thread(target=window_log, daemon=True).start()
    threading.Thread(target=window_counter, daemon=True).start()
    app.run(host='127.0.0.1', port=8080, debug=True)  # Change 8080 to your desired port
    
