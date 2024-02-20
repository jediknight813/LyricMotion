from moviepy.editor import AudioFileClip, VideoFileClip, concatenate_videoclips

from dotenv import load_dotenv
import os

load_dotenv()


from text_generation import text_generation
from audio_transcription import send_audio_for_transcription
from utils import pad_audio, trim_segments, loop_clip, stretch_clip
from image_generation import (
    create_animated_gif,
    create_animated_gif_hotshot_xl,
    create_animated_video,
)

VIDEO_STYLE = os.getenv("VIDEO_STYLE")
NEGATIVE_PROMPT = os.getenv("NEGATIVE_PROMPT")
VIDEO_PROMPT_STYLE = os.getenv("VIDEO_PROMPT_STYLE")


def create_video(
    audio_path,
    full_video=True,
    video_length=0,
    video_fps=16,
    video_style=VIDEO_STYLE,
    clip_method="Loop",
    negative_prompt=NEGATIVE_PROMPT,
    generate_lyric_prompts=True,
    useLocalGeneration=True,
    video_prompt_style=VIDEO_PROMPT_STYLE,
):
    # load audio
    audio_file = AudioFileClip(audio_path)

    # if we want the full video set it to the length of the audio
    if full_video == True:
        video_length = audio_file.duration

    # transcribe the audio
    audio_transcription = send_audio_for_transcription(audio_path)
    print("Audio transcribed.")

    # pad each segment of the audio transcription
    audio_transcription = pad_audio(audio_transcription)
    print("Padding audio.")

    # if we don't want the full video then we trim segments
    if full_video == False:
        audio_transcription = trim_segments(audio_transcription, video_length)

    # set the last segment to the length of the length of the video
    audio_transcription[-1]["end"] = video_length

    # print the number of clips to create.
    print("Clips to generate: ", len(audio_transcription))

    # check if we want to generate the prompts for the images based on the lyric
    if generate_lyric_prompts == True:

        # loop over each lyric and generate an image description for the lyric
        for lyric in audio_transcription:
            print("is using local text generation: ", useLocalGeneration)
            lyric["prompt"] = text_generation(
                lyric["text"], useLocalGeneration, video_style
            )
            print(
                "\nlyric: ",
                lyric["text"],
                "\nstart: ",
                lyric["start"],
                "\nend: ",
                lyric["end"],
                "\nprompt: ",
                lyric["prompt"],
            )

    # store all the paths to our generated clips
    video_clip_paths = []

    # create the video clips for each segment
    for index, segment in enumerate(audio_transcription):

        video_clip_save_path = "./video_clips/" + str(index) + ".mp4"

        if generate_lyric_prompts == True:
            print("generating gif with ai lyric prompt.")
            create_animated_video(segment["prompt"], video_clip_save_path)
            # create_animated_gif_hotshot_xl(
            #     segment["prompt"],
            #     832,
            #     512,
            #     video_clip_save_path,
            #     video_fps,
            #     negative_prompt,
            #     video_prompt_style,
            # )
        else:
            print("generating gif with lyric.")
            create_animated_video(
                segment["text"] + ", " + video_style, video_clip_save_path
            )
            # create_animated_gif_hotshot_xl(
            #     segment["text"] + ", " + video_style,
            #     832,
            #     512,
            #     video_clip_save_path,
            #     video_fps,
            #     negative_prompt,
            #     video_prompt_style,
            # )

        final_clip_save_path = "./video_clips/" + str(index) + "final.mp4"

        if clip_method == "Loop":
            loop_clip(
                (segment["end"] - segment["start"]),
                video_clip_save_path,
                final_clip_save_path,
                video_fps / 2,
            )
        if clip_method == "Stretch":
            stretch_clip(
                (segment["end"] - segment["start"]),
                video_clip_save_path,
                final_clip_save_path,
                video_fps / 2,
            )

        video_clip_paths.append(final_clip_save_path)

    # combine all of our clips with the video audio.
    video_clips = [VideoFileClip(path) for path in video_clip_paths]
    final_video = concatenate_videoclips(video_clips)
    audio_file = audio_file.set_duration(video_length)
    final_video = final_video.set_duration(video_length)
    final_video.audio = audio_file

    # to get a unique filename for the final video
    file_count = len(
        [
            f
            for f in os.listdir("./finished_videos")
            if os.path.isfile(os.path.join("./finished_videos", f))
        ]
    )

    final_video.write_videofile(
        "./finished_videos/" + str(file_count) + ".mp4",
        audio_codec="aac",
        fps=video_fps,
    )
    return "../finished_videos/" + str(file_count) + ".mp4"
