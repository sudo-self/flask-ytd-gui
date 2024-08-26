from flask import Flask, render_template, request, jsonify, send_from_directory
import subprocess
import os
import threading
import platform
import pyperclip
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO)

DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download_video', methods=['POST'])
def download_video():
    url = request.form.get('url')
    if url:
        threading.Thread(target=download_video_thread, args=(url,), daemon=True).start()
        return jsonify({'message': f'Started download for: {url}'})
    else:
        return jsonify({'error': 'No video URL input'}), 400

def download_video_thread(url):
    try:
        process = subprocess.Popen(
            ['yt-dlp', '-S', 'res,ext:mp4:m4a', '--recode', 'mp4', url, '-o', f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        out, err = process.communicate()
        update_terminal(out, err)
    except Exception as e:
        update_terminal('', str(e))

def update_terminal(out, err):
    terminal_output = out + err
    logging.info(terminal_output)

@app.route('/downloads')
def downloads():
    files = os.listdir(DOWNLOAD_FOLDER)
    return render_template('downloads.html', files=files)

@app.route('/downloads/<path:filename>')
def downloaded_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

@app.route('/open_directory')
def open_directory():
    directory = os.path.dirname(os.path.realpath(__file__))
    if platform.system() == 'Darwin':
        subprocess.Popen(['open', directory])
    elif platform.system() == 'Linux':
        subprocess.Popen(['xdg-open', directory])
    elif platform.system() == 'Windows':
        subprocess.Popen(['explorer', directory])
    return jsonify({'message': 'Opened directory'})

@app.route('/paste', methods=['POST'])
def paste_from_clipboard():
    try:
        clipboard_text = pyperclip.paste()
        if clipboard_text:
            return jsonify({'clipboard_text': clipboard_text})
        else:
            return jsonify({'error': 'Clipboard is empty or inaccessible'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/start_session', methods=['POST'])
def start_session():
    # Implement logic to start the session here
    return "Session started successfully"

@app.route('/stop_session', methods=['POST'])
def stop_session():
    # Implement logic to stop the session here
    return "Session stopped successfully"

if __name__ == '__main__':
    app.run(debug=True)

