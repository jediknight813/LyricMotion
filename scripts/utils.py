from moviepy.editor import concatenate_videoclips, VideoFileClip, vfx, AudioFileClip, clips_array
import os
from dotenv import load_dotenv
load_dotenv()


def pad_audio(segments):
    # set the start of the first segment to 0 secs.
    segments[0]["start"] = 0

    # loop over all the segments and set the end of each on to the start of the next segment.
    index = 0
    for segment in segments:
        if index+1 < len(segments):
            segment["end"] = segments[index+1]["start"]
            index += 1
    
    return segments


def trim_segments(segments, video_length):
    # remove lyrics that won't fit in the video length.
    final_list = []
    for segment in segments:
        # check if segment would fit in audio length
        if segment["end"] < video_length:
            final_list.append({"start": segment["start"], "end": segment["end"], "text": segment["text"]})
    
    return final_list


def loop_clip(duration, clip_path, save_path, video_framerate):
    clips_in_loop = []
    video = VideoFileClip(clip_path)
    reversed_video = video.fx(vfx.time_mirror)

    loops_needed = 0
    current_duration = 0
    while current_duration < duration:
        loops_needed += 1
        current_duration += video.duration

    print(loops_needed) 
    for loop_index in range(loops_needed):
        if loop_index % 2 == 0:
            clips_in_loop.append(video)
        else:
            clips_in_loop.append(reversed_video)

    final_video = concatenate_videoclips(clips_in_loop, method="compose")
    final_video = final_video.set_duration(duration)
    final_video.write_videofile(save_path, fps=video_framerate)


def stretch_clip(desired_duration, clip_path, save_path, video_framerate):
    clip = VideoFileClip(clip_path)

    current_duration = clip.duration
    speed_factor = current_duration / desired_duration
    stretched_clip = clip.fx(vfx.speedx, speed_factor)

    stretched_clip = stretched_clip.set_duration(desired_duration)
    stretched_clip.write_videofile(save_path, fps=video_framerate)

