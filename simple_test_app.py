from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from Railway! App is working."

@app.route('/health')
def health():
    return "OK", 200

@app.route('/ping')
def ping():
    return "OK", 200

@app.route('/test')
def test():
    return "Test endpoint working"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 4000))
    app.run(host='0.0.0.0', port=port) 