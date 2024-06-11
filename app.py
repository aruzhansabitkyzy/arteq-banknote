from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os
import subprocess
import logging
import sys

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join('static', 'uploads')
OUTPUT_FOLDER = os.path.join('static', 'videos')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_video', methods=['GET', 'POST'])
def upload_video():
    if request.method == 'POST':
        if 'video' not in request.files:
            logging.error('No video part in the request.')
            return redirect(request.url)
        video = request.files['video']
        if video.filename == '':
            logging.error('No selected file.')
            return redirect(request.url)
        filename = secure_filename(video.filename)
        video_path = os.path.join(UPLOAD_FOLDER, filename)
        video.save(video_path)
        logging.info(f'Video saved to {video_path}')
        
        # Define output path for processed video
        output_video_path = os.path.join(OUTPUT_FOLDER, filename)
        logging.info(f'Output video will be saved to {output_video_path}')
        
        # Run detection script # This gets the path to the current Python interpreter
        python_executable = sys.executable
        
        # Run detection script
        result = subprocess.run(
            [python_executable, 'detect.py', '--source', video_path, '--output', output_video_path],
            cwd=os.path.dirname(os.path.abspath(__file__)),  # Ensure the correct working directory
            capture_output=True,
            text=True
        )
        logging.info(f'Subprocess output: {result.stdout}')
        logging.error(f'Subprocess errors: {result.stderr}')
        
        if result.returncode != 0:
            logging.error('Error running detection script.')
            return f'Error running detection script: {result.stderr}', 500
        
        return redirect(url_for('display_video', filename=filename))
    return render_template('upload_video.html')



@app.route('/display_video/<filename>')
def display_video(filename):
    logging.info(f'Displaying video: {filename}')

    return render_template('display_video.html', filename=filename)

@app.route('/live_detection', methods=['GET'])
def live_detection():
    output_video_path = os.path.join(OUTPUT_FOLDER, 'live_output.mp4')
    result = subprocess.run(['python', 'detect.py', '--source', '0', '--output', output_video_path], capture_output=True, text=True)
    logging.info(f'Subprocess output: {result.stdout}')
    logging.error(f'Subprocess errors: {result.stderr}')
    return render_template('live_detection.html')

@app.route('/static/videos/<filename>')
def send_video(filename):
    logging.info(f'Sending video: {filename}')
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)
