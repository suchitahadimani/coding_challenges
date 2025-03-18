from flask import Flask, jsonify, request, json
import requests
import threading
import time


app = Flask(__name__)

ALL_SERVER_URLS = ["http://127.0.0.1:9090", "http://127.0.0.1:9091"] 
ALIVE_SERVER_URLS = ["http://127.0.0.1:9090", "http://127.0.0.1:9091"] 
DEAD_SERVER_URLS = []
TIMEOUT = 1

lock = threading.Lock()

n = 0
def roundrobin():
    global n
    with lock:
        if ALIVE_SERVER_URLS:
            url = ALIVE_SERVER_URLS[n]
            n += 1
            if n == len(ALIVE_SERVER_URLS):
                n = 0

            return url
        
        return None

def health_check():
    while True:
        time.sleep(0.5)
        

        for url in ALL_SERVER_URLS:
            try:
                response = requests.get(f"{url}/health", timeout=TIMEOUT)  
                if response.status_code == 200:
                    with lock:
                        if url in DEAD_SERVER_URLS:
                            DEAD_SERVER_URLS.remove(url)
                            ALIVE_SERVER_URLS.append(url)
            
            except requests.exceptions.RequestException as e:
                with lock:
                    if url in ALIVE_SERVER_URLS:
                        ALIVE_SERVER_URLS.remove(url)
                        DEAD_SERVER_URLS.append(url)


@app.route("/", methods=["GET"])
def forwarder():
    try:
        #requests are used for making essentially anytype of api call and can be used for forwarding to a different server too.
        url = roundrobin()

        if url is None:
            return jsonify({"message": "No available servers"}), 503
        
        response = requests.get(f"{url}")  
        return  jsonify({"message": f"{json.loads(response.text)['message']}"}), response.status_code 
    
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    threading.Thread(target=health_check, daemon=True).start() 
    app.run(host='127.0.0.1', port=8080, debug=True)  