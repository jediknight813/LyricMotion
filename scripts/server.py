from flask import Flask, request, jsonify, send_file
import logging
import sys
from video_creation import create_video
from gevent.pywsgi import WSGIServer

import os
from dotenv import load_dotenv
load_dotenv()

VIDEO_STYLE = os.getenv("VIDEO_STYLE")
NEGATIVE_PROMPT = os.getenv("NEGATIVE_PROMPT")
VIDEO_PROMPT_STYLE = os.getenv("VIDEO_PROMPT_STYLE")

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

@app.route('/create_lyric_video', methods=['POST'])
def create_lyric_video():
    # Check if the request contains a file
    if 'audio_file' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio_file']

    # Check if the file is allowed
    if audio_file.filename == '' or '.' not in audio_file.filename:
        return jsonify({'error': 'Invalid file'}), 400

    # Extract the file extension
    file_extension = audio_file.filename.rsplit('.', 1)[1].lower()

    # Check if the file extension is allowed
    if file_extension not in {'mp3', 'wav', 'ogg'}:
        return jsonify({'error': 'Invalid file format'}), 400

    # Save the file to the 'audio' folder
    audio_file_path = os.path.join("./audio/"+audio_file.filename )
    audio_file.save(audio_file_path)

    # Get other parameters from the request
    full_video = request.form.get('full_video', type=lambda x: x.lower() == 'true', default=False)
    video_length = request.form.get('video_length', type=int, default=10)
    video_fps = request.form.get('video_fps', type=int, default=16)
    video_style = request.form.get('video_style', default=VIDEO_STYLE)
    clip_method = request.form.get('clip_method', default="Loop")
    negative_prompt = request.form.get('negative_prompt', default=NEGATIVE_PROMPT)
    generate_lyric_prompts = request.form.get('generate_lyric_prompts', type=lambda x: x.lower() == 'true', default=True)
    use_local_generation = request.form.get('useLocalGeneration', type=lambda x: x.lower() == 'true', default=True)
    video_prompt_style = request.form.get('video_prompt_style', default=VIDEO_PROMPT_STYLE)

    # generate the video
    try:
        video_file_path = create_video(audio_file_path, full_video, video_length, video_fps, video_style, clip_method, negative_prompt, generate_lyric_prompts, use_local_generation, video_prompt_style)
    except Exception as error:
        error_message = str(error)
        print(error_message)
        return {"message": error_message}
        
    return send_file(video_file_path, as_attachment=True)


if __name__ == '__main__':
    http_server = WSGIServer(('', 8787), app)
    http_server.serve_forever()

