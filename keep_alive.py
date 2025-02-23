from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "I'm Alive\nHello World!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    server = threading.Thread(target=run)
    server.start()
