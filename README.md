# LyricMotion
![tmph7i6quqp](https://github.com/jediknight813/animated-lyric-video-builder/assets/17935336/8c2be248-27cb-43e2-9e60-35e63be26845)

LyricMotion is an innovative animated lyric video builder that transforms music into visually stunning AI-generated videos. 
Bring your lyrics to life with dynamic animations synchronized to the rhythm of your music.


https://github.com/jediknight813/animated-lyric-video-builder/assets/17935336/a232aa0a-02a3-402c-bffa-f03cb32ac1d1

# LyricMotion Prerequisites
Before you start using LyricMotion, make sure you have the following requirements ready:

### llama-cpp-python Server
llama-cpp-python: Follow the instructions in the repository to set up and run the server.

https://github.com/abetlen/llama-cpp-python


### Stable Diffusion WebUI with Hotshot-XL-Automatic1111 Extension

Stable Diffusion WebUI: Clone the repository and install dependencies following the provided instructions.

https://github.com/AUTOMATIC1111/stable-diffusion-webui


Hotshot-XL-Automatic1111: Clone and setup this extension into the extensions directory of Stable Diffusion WebUI.

https://github.com/hotshotco/Hotshot-XL-Automatic1111

Note: Make sure both the llama-cpp-python server and the Stable Diffusion WebUI with the Hotshot-XL-Automatic1111 extension are up and running before using LyricMotion.

# Setup

### fill in your .env file
```python
WHISPER_API_IP=""

LOCAL_TEXT_GENERATION_URL=
LOCAL_IMAGE_GENERATION_URL=

OPENAI_API_KEY=
OPENAI_ORGANIZATION=

VIDEO_PROMPT_STYLE=
VIDEO_STYLE=""
NEGATIVE_PROMPT=""
```

You can run the server locally or with docker.

### how to run it locally.
```python
pip install requirements.txt
python scripts/server.py
```

### how to run it with docker.
```python
docker build -t animated-video-builder:latest .
```

### Creating a video

you can create a video with the server running with this function.

```python
def create_video_request(audio_file_path, full_video=True, video_length=8, video_fps=8,
                          video_style="VIDEO_STYLE", clip_method="Loop", negative_prompt="NEGATIVE_PROMPT",
                          generate_lyric_prompts=False, use_local_generation=False, video_file_path="./finished_videos/video.mp4"):

    # Set the Flask server URL
    server_url = # replace with your ip.

    data = {
        'full_video': full_video,
        'video_length': video_length,
        'video_fps': video_fps,
        'video_style': video_style,
        'clip_method': clip_method,
        'negative_prompt': negative_prompt,
        'generate_lyric_prompts': generate_lyric_prompts,
        'useLocalGeneration': use_local_generation,
    }

    with open(audio_file_path, 'rb') as audio_file:
        files = {'audio_file': (audio_file)}
        response = requests.post(server_url, data=data, files=files)
    video_file.write(response.content)
```
