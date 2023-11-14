import requests
import os
from moviepy.editor import ImageSequenceClip
from dotenv import load_dotenv
import base64
from PIL import Image
from io import BytesIO
import numpy as np
load_dotenv()


LOCAL_IMAGE_GENERATION_URL = os.getenv("LOCAL_IMAGE_GENERATION_URL")


def create_animated_gif(prompt, width, height, save_path, video_framerate, negative_prompt, video_style):
    create_animation_url = "http://"+LOCAL_IMAGE_GENERATION_URL+":7860/sdapi/v1/txt2img"

    # A1111 payload
    payload = {
        "prompt": video_style+prompt,
        "steps": 25,
        "negative_prompt": negative_prompt,
        "width": width,
        "height": height,
        "sampler_index": "Euler a",
        "cfg_scale": 7,

        'alwayson_scripts': {
            'AnimateDiff': {
                'args': [{
                'model': 'mm_sd_v15_v2.ckpt', 
                'format': ['PNG'],   
                'enable': True,    
                'video_length': video_framerate,   
                'fps': 8,            
                'loop_number': 0,     
                'closed_loop': 'R+P',  
                'batch_size': 16, 
                'stride': 1,   
                'overlap': -1,  
                'interp': 'Off',
                'interp_x': 10,
                'video_source': '',  
                'video_path': '',      
                'latent_power': 0,    
                'latent_scale': 0,    
                'last_frame': None,    
                'latent_power_last': 0,
                'latent_scale_last': 0
                }]
            }
        }
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


def create_animated_gif_hotshot_xl(prompt, width, height, save_path, video_framerate, negative_prompt, video_style):
    create_animation_url = "http://"+LOCAL_IMAGE_GENERATION_URL+":7860/sdapi/v1/txt2img"

    # A1111 payload
    payload = {
        "prompt": video_style+prompt,
        "steps": 25,
        "negative_prompt": negative_prompt,
        "width": width,
        "height": height,
        "sampler_index": "Euler a",
        "cfg_scale": 7,
    
        'alwayson_scripts': {
            'Hotshot-XL': {
                'args': [{
                'model': 'hsxl_temporal_layers.f16.safetensors', 
                'format': ['PNG'],   
                'enable': True,    
                'video_length': video_framerate,   
                'fps': video_framerate,            
                'loop_number': 0,     
                'batch_size': 8, 
                "reverse": [],
                'stride': 1,   
                'overlap': -1,  
                'original_size_width': 1920,
                'original_size_height': 1080,
                'target_size_width': 512,
                'target_size_height': 512,
                'negative_original_size_width':1920,
                'negative_original_size_height':1080,
                'negative_target_size_width':512,
                'negative_target_size_height':512,
                }]
            }
        }
    }

    response = requests.post(url=create_animation_url, json=payload)
    r = response.json()
    base64_images = r["images"]
    print("images created: ",str(len(base64_images)))

    image_list = []
    for base64_string in base64_images:
        image_data = base64.b64decode(base64_string)
        image = Image.open(BytesIO(image_data))
        image_list.append(np.array(image))
    
    video_clip = ImageSequenceClip(image_list, fps=8)
    video_clip.write_videofile(save_path, codec="libx264")

