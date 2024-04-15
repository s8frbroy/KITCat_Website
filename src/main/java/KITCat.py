from flask import Flask, send_from_directory
import os

app = Flask(__name__)

# Serve static files from the 'static' directory
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

# Define route for /hello
@app.route('/hello')
def hello():
    return 'Hello World'

# Define route for /VoiceRecorder
@app.route('/VoiceRecorder')
def voice_recorder():
    # Read the contents of the HTML file
    html_file_path = os.path.join(os.path.dirname(__file__), 'VoiceRecorder.html')
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return html_content
    except FileNotFoundError:
        # If the HTML file doesn't exist, return 404 Not Found
        return 'HTML file not found', 404

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True)
