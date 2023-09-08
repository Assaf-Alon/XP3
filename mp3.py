import pytube
from moviepy.editor import *

from mp3_metadata import Song, update_metadata_from_song
from constants import MP3_DIR, MP4_DIR, DEFAULT_PLAYLIST

from os import listdir
from os.path import isfile, join, basename


def get_playlist_songs(
    playlist_url: str = DEFAULT_PLAYLIST,
    start_index: int = 0,
    end_index: int = 999999,
    interactive: bool = True,
    update_album: bool = True,
):
    playlist = pytube.Playlist(playlist_url)
    print(f"Number of videos in playlist: {len(playlist.video_urls)}")
    start_index -= 1
    end_index = min(end_index - 1, len(playlist.video_urls))

    songs = []

    for index in range(start_index, end_index + 1):
        py_video = playlist.videos[index]
        song = Song(py_video.watch_url, py_video.title, py_video.author)
        song.fix_title(interactive=interactive)
        if update_album:
            song.update_album_info(interactive=interactive)
            song.update_image()
        songs.append(song)

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
    verbose: bool = True,
):
    songs = get_playlist_songs(
        playlist_url=playlist_url, start_index=start_index, end_index=end_index
    )
    for song in songs:
        if verbose:
            print(f" > Downloading {song.title}, from {song.url}")
        filename = download_ytvid(song.url, out_path=MP4_DIR, title=song.title)
        if verbose:
            print(f" >> Downloaded {filename}")
        convert_mp4_to_mp3(mp4_path=filename)
        update_metadata_from_song(MP3_DIR, song)
        if verbose:
            print(f" >> Updated metadata for {filename}")
