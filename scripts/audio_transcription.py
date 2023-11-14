import requests
from dotenv import load_dotenv
import os
load_dotenv()


WHISPER_API_IP = os.getenv("WHISPER_API_IP")

def send_audio_for_transcription(audio_file_path, encode=True, task='transcribe', language='en', word_timestamps=True, output='json'):
    url = f'http://{WHISPER_API_IP}:9000/asr?encode={encode}&task={task}&language={language}&word_timestamps={word_timestamps}&output={output}'
    headers = {
        'accept': 'application/json',
    }
    files = {'audio_file': ('Joe.mp3', open(audio_file_path, 'rb'), 'audio/mpeg')}

    response = requests.post(url, headers=headers, files=files)

    if response.status_code == 200:
        response = response.json()
        print(len(response["segments"]))
        print(response["segments"])
        return response["segments"]
    else:
        print(f"Error: {response.status_code}")
        return None
