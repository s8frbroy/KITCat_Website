import sys
from flask import Flask, send_from_directory, request, jsonify, render_template
import os
import subprocess
import logging
import json
import requests

app = Flask(__name__)

# Ensure the upload directory exists
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Serve static files from the 'static' directory
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

# Define route for /hello
@app.route('/hello')
def hello():
    return 'Hello World'

# Define route for /VoiceRecorder
@app.route('/')
def voice_recorder():

    d = {'log': 'True', 'error_correction': False, 'asr_prop': {}, 'mt_prop': {}, 'prep_prop': {}, 'textseg_prop': {}, 'tts_prop': {}, 'lip_prop': {}}
    # Read the contents of the HTML file
    url = "http://lt2srv-backup.iar.kit.edu/"#"http://frederik:frederik@i13hpc60:8208"
    api = "webapi"
    token = 'NDGIIwFB3s30200JJl0jMkgkdcaZ4IxsPWud3-DDEMQ=|1722515904|uzhgc@student.kit.edu'
    sessionID, streamID = 1,2
    print(url +api+"/get_default_asr")
    res = requests.post(url +api+"/get_default_asr", json=json.dumps(d), cookies={'_forward_auth': token})
    #res = requests.post("http://lt2srv-backup.iar.kit.edu//webapi/get_default_asr", json=json.dumps(d), cookies={'_forward_auth': token})
    print("---> Default graph for ASR send")
    if res.status_code != 200:
        if res.status_code == 401:
            print("You are not authorized. Either authenticate with --url https://$username:$password@$server or with --token $token where you get the token from "+args.url+"/gettoken")
        else:
            print(res.status_code,res.text)
            print("ERROR in requesting default graph for ASR")
        sys.exit(1)
    sessionID, streamID = res.text.split()
    print("SessionId",sessionID,"StreamID",streamID)
    
    # Read the contents of the HTML file
    return render_template('VoiceRecorder.html', sessionID=sessionID, streamID=streamID, server = url, api = api)
    # html_file_path = os.path.join(os.path.dirname(__file__), 'OLD_VoiceRecorder.html')
    # try:
    #     with open(html_file_path, 'r', encoding='utf-8') as f:
    #         html_content = f.read()
    #     return html_content
    # except FileNotFoundError:
    #     # If the HTML file doesn't exist, return 404 Not Found
    #     return 'HTML file not found', 404
    
# Define route for /audio
@app.route('/audio')
def audio():
    
    html_file_path = os.path.join(os.path.dirname(__file__), 'audio.html')
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return html_content
    except FileNotFoundError:
        # If the HTML file doesn't exist, return 404 Not Found
        return 'HTML file not found', 404

# Define route for /VoiceRecorder
@app.route('/continous')
def continous():
    # Read the contents of the HTML file
    html_file_path = os.path.join(os.path.dirname(__file__), 'ContinousStreaming.html')
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return html_content
    except FileNotFoundError:
        # If the HTML file doesn't exist, return 404 Not Found
        return 'HTML file not found', 404

@app.route('/process-audio', methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return jsonify({'message': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    print(f"Process audio to Send to backend!!!")
    print(audio_file.filename)
    print(type(audio_file))
    file_path = os.path.join(UPLOAD_FOLDER, audio_file.filename)
    audio_file.save(file_path)

    try:
     # Run the Python script with the audio file as an argument
        result = subprocess.run(
            ['python3', 'website_python/audioClient/audio_client_website.py', 
             '-f', file_path, 
             '-u', 'http://frederik:frederik@i13hpc60:8090'],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return jsonify({'message': 'Python script execution failed', 'error': result.stderr}), 500

        return jsonify({'message': 'Python script executed successfully', 'output': result.stdout}), 200

    except subprocess.CalledProcessError as e:
        return jsonify({'message': 'Python script execution failed', 'error': e.stderr}), 500
    except Exception as e:
        return jsonify({'message': 'An unexpected error occurred', 'error': str(e)}), 500


# Define a route for executing the Python script
@app.route('/execute-python-script', methods=['POST'])
def execute_python_script():
    # Extract any data sent from the client
    try:
        data = request.get_json()

        if 'audio' not in data:
            return jsonify({'error': 'No audio data provided'}), 400

        audio_data = data['audio']
        logging.info("Attempting to run the Python script")
        result = subprocess.run(
            ['/Users/frbroy/miniconda3/envs/hiwi_env/bin/python', 'website_python/audioClient/audio_client_website.py',
              "-f", "website_python/audioClient/oneminute.mp4", "-u", "http://frederik:frederik@i13hpc60:8090", "-i", "website",
                "-audio", audio_data]
        )
        logging.info("Script output: %s", result.stdout)
        return jsonify({'message': 'Python script executed successfully', 'output': result.stdout}), 200
    
    except subprocess.CalledProcessError as e:
        logging.error("Script failed with error: %s", e.stderr)
        return jsonify({'message': 'Python script execution failed', 'error': e.stderr}), 500
    except Exception as e:
        logging.error("An unexpected error occurred: %s", str(e))
        return jsonify({'message': 'An unexpected error occurred', 'error': str(e)}), 500




if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True)

    # Make sure to configure logging to capture the output
    logging.basicConfig(level=logging.INFO)
