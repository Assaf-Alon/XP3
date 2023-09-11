import pytube
from moviepy.editor import *

from mp3_metadata import Song, update_metadata_from_song
from constants import MP3_DIR, MP4_DIR, DEFAULT_PLAYLIST, IS_DEBUG

from os import listdir
from os.path import isfile, join, basename

import logging
from typing import Tuple, List

logger = logging.getLogger("XP3")
logger.setLevel(logging.DEBUG if IS_DEBUG else logging.INFO)


def get_playlist_songs(
    playlist_url: str = DEFAULT_PLAYLIST,
    start_index: int = 0,
    end_index: int = 999999,
    interactive: bool = True,
    update_album: bool = True,
) -> List[Tuple[Song, str]]:
    playlist = pytube.Playlist(playlist_url)

    logger.debug(f"Number of videos in playlist: {len(playlist.video_urls)}")
    start_index -= 1
    end_index = min(end_index - 1, len(playlist.video_urls))

    songs = []

    for index in range(start_index, end_index + 1):
        py_video = playlist.videos[index]
        song = Song(
            title=py_video.title, channel=py_video.author, interactive=interactive
        )
        if update_album:
            song.update_album_info(interactive=interactive)
            song.update_image()
        songs.append((song, py_video.watch_url))

    return songs


def download_ytvid(video_url: str, out_path: str = MP4_DIR, title: str = None):
    if title and not title.endswith(".mp4"):
        title = title + ".mp4"
    return (
        pytube.YouTube(video_url)
        .streams.filter(file_extension="mp4")
        .first()
        .download(output_path=out_path, filename=title)
    )


def convert_mp4_to_mp3(mp4_path: str):
    assert mp4_path.endswith(".mp4")
    mp4_filename = basename(mp4_path)
    mp3_path = join(MP3_DIR, mp4_filename[:-1] + "3")
    video = VideoFileClip(mp4_path)
    video.audio.write_audiofile(mp3_path)


def download_XPrimental(
    playlist_url: str = DEFAULT_PLAYLIST,
    start_index: int = 0,
    end_index: int = 99999,
    interactive: bool = True,
):
    songs = get_playlist_songs(
        playlist_url=playlist_url, start_index=start_index, end_index=end_index
    )
    for song, url in songs:
        logger.debug(f" > Downloading {song.title}, from {url}")
        filename = download_ytvid(url, out_path=MP4_DIR, title=song.title)
        logger.debug(f" >> Downloaded {filename}")
        convert_mp4_to_mp3(mp4_path=filename)
        update_metadata_from_song(MP3_DIR, song)
        logger.debug(f" >> Updated metadata for {filename}")
