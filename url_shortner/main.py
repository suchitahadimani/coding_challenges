from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import base64
import uuid
import hashlib
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change to frontend URL in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

long_short = dict()
short_long = dict()
regex = r"\b(ht{1,2}ps?:\/\/?)\b"

# Serve static files (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

class InputData(BaseModel):
    text: str

@app.get("/", response_class=HTMLResponse)
def serve_ui():
    with open("static/index.html", "r") as f:
        return f.read()

@app.post("/submit")
def handle_input(data: InputData):

    if('.' in data.text):
        if(data.text in long_short ):
            return {"message": f"{long_short[data.text]}"} 

        matches = re.finditer(regex, data.text)
        for match in matches:
            end_index = match.end()
            data = data.text[end_index:]
        else:
            data = data.text
        data = "https://"+data
        salted_input = data + str(uuid.uuid4())  
        sha256_hash = hashlib.sha256(salted_input.encode()).digest()
        pin = base64.urlsafe_b64encode(sha256_hash)[:8].decode()
        long_short[data] = pin
        short_long[pin]=data

        return {"message": f"{pin}"}
    else:
        return {"message": f"Invalid URL"}
        
@app.get("/{pin}")
def redirect_to_long_url(pin: str):
    if pin in short_long:
        return RedirectResponse(url=short_long[pin])
    else:
        raise HTTPException(status_code=404, detail="URL not found")