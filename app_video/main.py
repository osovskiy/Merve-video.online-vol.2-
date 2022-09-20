from typing import List
import os
import logging
from random import randint
from urllib.error import HTTPError


from fastapi import FastAPI
from pytube import YouTube, Playlist
from moviepy.editor import VideoFileClip, concatenate_videoclips
from pytube.helpers import safe_filename
import uvicorn

from schemas import Video, PlayList

app = FastAPI()


# Playlist download function
@app.post("/playlist")
def create_playlist(item: PlayList):
    videos = []
    size = []
    for video in item.link:
        pl = Playlist(video)
        links = [i for i in pl]
        for l in links:
            try:
                yt = YouTube(l)
                stream = yt.streams.filter(progressive=True, res="720p")[0]
                stream.download()
                name = f'{safe_filename(yt.title)}.mp4'
                videos.append(name)
                file_states = os.stat(name)
                size.append(file_states.st_size)
            except IndexError:
                stream = yt.streams.filter(progressive=True)[1]
                stream.download()
                name = f'{safe_filename(yt.title)}.mp4'
                videos.append(name)
                file_states = os.stat(name).st_size
                size.append(file_states)
            except HTTPError:
                continue

    try:
        return {"videos": videos, "size": sum(size) / 1000000}
    except Exception as ex:
        return ex


# Video download function
@app.post('/video')
def create_video(item: Video):
    videos = []
    size = []
    links = item.link
    for l in links:
        yt = YouTube(l)
        try:
            stream = yt.streams.filter(progressive=True, res="720p")[0]
            stream.download()
            name = f'{safe_filename(yt.title)}.mp4'
            videos.append(name)
            file_states = os.stat(name)
            size.append(file_states.st_size)
        except IndexError:
            stream = yt.streams.filter(progressive=True)[1]
            stream.download()
            name = f'{safe_filename(yt.title)}.mp4'
            videos.append(name)
            file_states = os.stat(name)
            size.append(file_states.st_size)
        except HTTPError:
            continue

    try:
        return {"videos": videos, "size": sum(size) / 1000000}
    except Exception as ex:
        return ex

# Source merging function


@app.post('/create')
def create(videos: list, names: str):
    r_videos = []
    for video in videos:
        r_v = VideoFileClip(video)
        r_videos.append(r_v)
    try:
        final_clip = concatenate_videoclips(r_videos, method="compose")
        final_clip.write_videofile(f"{names}.mp4")
        try:
            for video in videos:
                os.remove(video)
        except:
            pass
        p = os.path.abspath(f"{names}.mp4")
        return p
    except Exception as ex:
        print("Ничего не вышло :(")
        print(ex)

# Delete source function


@app.post('/delete')
def delete(videos: list):
    for video in videos:
        os.remove(video)


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR, filename="log.txt")
    uvicorn.run(app, port=8080)
