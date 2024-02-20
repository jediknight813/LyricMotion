import requests
import os
from moviepy.editor import ImageSequenceClip
from dotenv import load_dotenv
import base64
from PIL import Image
from io import BytesIO
import numpy as np
import websocket
import uuid
import json
import urllib.request
import urllib.parse
import tempfile
from moviepy.editor import (
    VideoFileClip,
)

load_dotenv()


LOCAL_IMAGE_GENERATION_URL = os.getenv("LOCAL_IMAGE_GENERATION_URL")
server_address = str(LOCAL_IMAGE_GENERATION_URL) + ":18188"
client_id = str(uuid.uuid4())


def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode("utf-8")
    req = urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    return json.loads(urllib.request.urlopen(req).read())


def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(
        "http://{}/view?{}".format(server_address, url_values)
    ) as response:
        return response.read()


def get_history(prompt_id):
    with urllib.request.urlopen(
        "http://{}/history/{}".format(server_address, prompt_id)
    ) as response:
        return json.loads(response.read())


def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)["prompt_id"]
    output_images = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message["type"] == "executing":
                data = message["data"]
                if data["node"] is None and data["prompt_id"] == prompt_id:
                    break  # Execution is done
        else:
            continue  # previews are binary data

    history = get_history(prompt_id)[prompt_id]
    for o in history["outputs"]:
        for node_id in history["outputs"]:
            node_output = history["outputs"][node_id]
            if "gifs" in node_output:
                images_output = []
                for image in node_output["gifs"]:
                    image_data = get_image(
                        image["filename"], image["subfolder"], image["type"]
                    )
                    images_output.append(image_data)

                output_images[node_id] = images_output

    return output_images


def create_animated_video(positive_prompt, save_path, motion_level=150):
    print(uuid)
    print(save_path)
    prompt_workflow = json.load(open("./workflows/lcmtext2vid.json"))
    prompt = prompt_workflow
    prompt["52"]["inputs"]["text"] = positive_prompt
    prompt["12"]["inputs"]["motion_bucket_id"] = motion_level

    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    images = get_images(ws, prompt)

    for node_id in images:
        for video_data in images[node_id]:
            video_array = np.frombuffer(video_data, dtype=np.uint8)
            temp_filename = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            temp_filename.write(video_array)
            temp_filename.close()

            clip = VideoFileClip(temp_filename.name)
            clip.write_videofile(
                save_path,
                codec="libx264",
                audio_codec="aac",
                temp_audiofile="temp-audio.m4a",
                remove_temp=True,
                fps=clip.fps,
            )

            import os

            os.remove(temp_filename.name)

    return "finished"


def create_animated_gif(
    prompt, width, height, save_path, video_framerate, negative_prompt, video_style
):
    create_animation_url = (
        "http://" + LOCAL_IMAGE_GENERATION_URL + ":7860/sdapi/v1/txt2img"
    )

    # A1111 payload
    payload = {
        "prompt": video_style + prompt,
        "steps": 25,
        "negative_prompt": negative_prompt,
        "width": width,
        "height": height,
        "sampler_index": "Euler a",
        "cfg_scale": 7,
        "alwayson_scripts": {
            "AnimateDiff": {
                "args": [
                    {
                        "model": "mm_sd_v15_v2.ckpt",
                        "format": ["PNG"],
                        "enable": True,
                        "video_length": video_framerate,
                        "fps": 8,
                        "loop_number": 0,
                        "closed_loop": "R+P",
                        "batch_size": 16,
                        "stride": 1,
                        "overlap": -1,
                        "interp": "Off",
                        "interp_x": 10,
                        "video_source": "",
                        "video_path": "",
                        "latent_power": 0,
                        "latent_scale": 0,
                        "last_frame": None,
                        "latent_power_last": 0,
                        "latent_scale_last": 0,
                    }
                ]
            }
        },
    }

    response = requests.post(url=create_animation_url, json=payload)
    r = response.json()
    base64_images = r["images"]
    print(len(base64_images))

    image_list = []
    for base64_string in base64_images:
        image_data = base64.b64decode(base64_string)
        image = Image.open(BytesIO(image_data))
        image_list.append(np.array(image))

    video_clip = ImageSequenceClip(image_list, fps=8)
    video_clip.write_videofile(save_path, codec="libx264")


def create_animated_gif_hotshot_xl(
    prompt, width, height, save_path, video_framerate, negative_prompt, video_style
):
    create_animation_url = (
        "http://" + LOCAL_IMAGE_GENERATION_URL + ":7860/sdapi/v1/txt2img"
    )

    # A1111 payload
    payload = {
        "prompt": video_style + prompt,
        "steps": 25,
        "negative_prompt": negative_prompt,
        "width": width,
        "height": height,
        "sampler_index": "Euler a",
        "cfg_scale": 7,
        "alwayson_scripts": {
            "Hotshot-XL": {
                "args": [
                    {
                        "model": "hsxl_temporal_layers.f16.safetensors",
                        "format": ["PNG"],
                        "enable": True,
                        "video_length": video_framerate,
                        "fps": video_framerate,
                        "loop_number": 0,
                        "batch_size": 8,
                        "reverse": [],
                        "stride": 1,
                        "overlap": -1,
                        "original_size_width": 1920,
                        "original_size_height": 1080,
                        "target_size_width": 512,
                        "target_size_height": 512,
                        "negative_original_size_width": 1920,
                        "negative_original_size_height": 1080,
                        "negative_target_size_width": 512,
                        "negative_target_size_height": 512,
                    }
                ]
            }
        },
    }

    response = requests.post(url=create_animation_url, json=payload)
    r = response.json()
    base64_images = r["images"]
    print("images created: ", str(len(base64_images)))

    image_list = []
    for base64_string in base64_images:
        image_data = base64.b64decode(base64_string)
        image = Image.open(BytesIO(image_data))
        image_list.append(np.array(image))

    video_clip = ImageSequenceClip(image_list, fps=8)
    video_clip.write_videofile(save_path, codec="libx264")
