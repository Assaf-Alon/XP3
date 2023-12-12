"""Functions used to get data related to mp3 files and download them"""
import logging
from os.path import basename, join
from typing import List, Optional, Tuple

import pytube
from moviepy.editor import VideoFileClip

from config import DEFAULT_PLAYLIST, IS_DEBUG, MP3_DIR, MP4_DIR
from mp3_metadata import MP3MetaData

logging.basicConfig()
logger = logging.getLogger("XP3")
logger.setLevel(logging.DEBUG if IS_DEBUG else logging.INFO)


def get_playlist_songs(
    playlist_url: str = DEFAULT_PLAYLIST,
    start_index: int = 1,
    end_index: int = 999999,
    interactive: bool = True,
    update_album: bool = True,
) -> List[Tuple[MP3MetaData, str]]:
    """Given a YouTube playlist URL, returns a list of mp3 data
       of the songs in that playlist and the associated URL.

    Args:
        playlist_url (str, optional): The URL of the playlist. Defaults to DEFAULT_PLAYLIST (from config).
        start_index (int, optional): The index of the first song from the playlist. Defaults to 1.
        end_index (int, optional): The index of the last song from the playlist. Defaults to 999999.
        interactive (bool, optional): Should run in interactive mode and ask user for input regarding title conversion.
                                      Defaults to True.
        update_album (bool, optional): Should update album metadata. Defaults to True.

    Returns:
        List[Tuple[MP3MetaData, str]]: List of tuples - metadata regarding the song, and the song's URL.
    """
    playlist = pytube.Playlist(playlist_url)

    logger.debug("Number of videos in playlist: %d", len(playlist.video_urls))
    start_index -= 1
    end_index = min(end_index - 1, len(playlist.video_urls))

    songs = []
    videos = list(playlist.videos)
    for index in range(start_index, end_index + 1):
        py_video = videos[index]
        metadata = MP3MetaData.from_video(title=py_video.title, channel=py_video.author, interactive=interactive)
        if update_album:
            metadata.update_missing_fields(interactive=interactive)
            metadata.update_album_art()
        songs.append((metadata, py_video.watch_url))

    return songs


def download_ytvid(video_url: str, out_path: str = MP4_DIR, title: Optional[str] = None) -> Optional[str]:
    """Downloads a video from YouTube

    Args:
        video_url (str): The URL of the video
        out_path (str, optional): Base path of the downloaded video. Defaults to MP4_DIR.
        title (Optional[str], optional): File name of the downloaded video. If None, uses video title. Defaults to None.

    Returns:
        Optional[str]: Path to saved video if succeeded
    """
    if title and not title.endswith(".mp4"):
        title = title + ".mp4"
    mp4_stream = pytube.YouTube(video_url).streams.filter(file_extension="mp4").first()
    if not mp4_stream:
        logger.error("No stream found for %s", video_url)
        return None
    return mp4_stream.download(output_path=out_path, filename=title)


def convert_mp4_to_mp3(mp4_path: str) -> Optional[str]:
    """Converts an mp4 file to an mp3 file.

    Args:
        mp4_path (str): Path to the input mp4 file.

    Returns:
        Optional[str]: Path to the output mp3 file.
    """
    assert mp4_path.endswith(".mp4")
    mp4_filename = basename(mp4_path)
    mp3_path = join(MP3_DIR, mp4_filename[:-1] + "3")
    video = VideoFileClip(mp4_path)
    if not video.audio:
        logger.error("Audio not found for %s", mp4_path)
        return None
    video.audio.write_audiofile(mp3_path)
    return mp3_path


def download_song(
    song_url: str,
    update_album: bool = True,
    interactive: bool = True,
):
    """Downloads a single song and updates its metadata

    Args:
        song_url (str): The URL of the song
        update_album (bool, optional): Whether to update album metadata or not. Defaults to True.
        interactive (bool, optional): Whether to run metadata updates in interactive mode. Defaults to True.
    """
    py_video = pytube.YouTube(song_url)
    metadata = MP3MetaData.from_video(title=py_video.title, channel=py_video.author, interactive=interactive)
    if update_album:
        metadata.update_missing_fields(interactive=interactive)
        metadata.update_album_art()
    logger.debug(" > Downloading %s, from %s", metadata.title, song_url)
    filename = download_ytvid(song_url, out_path=MP4_DIR, title=metadata.title)
    if not filename:
        return

    logger.debug(" >> Downloaded %s", filename)
    mp3_path = convert_mp4_to_mp3(mp4_path=filename)
    if not mp3_path:
        return

    metadata.apply_on_file(mp3_path)
    logger.debug(" >> Updated metadata for %s", mp3_path)


def download_xprimental(
    playlist_url: str = DEFAULT_PLAYLIST,
    start_index: int = 1,
    end_index: int = 99999,
    interactive: bool = True,
):
    """Downloads songs from a playlist.

    Args:
        playlist_url (str, optional): The URL of the playlist. Defaults to DEFAULT_PLAYLIST.
        start_index (int, optional): The index of the first song to download. Defaults to 1.
        end_index (int, optional): The index of the last song to download. Defaults to 99999.
        interactive (bool, optional): Should run in interactive mode and ask user for input regarding title conversion.
                                      Defaults to True.
    """
    songs = get_playlist_songs(
        playlist_url=playlist_url, start_index=start_index, end_index=end_index, interactive=interactive
    )
    for metadata, url in songs:
        logger.debug(" > Downloading %s, from %s", metadata.title, url)
        filename = download_ytvid(url, out_path=MP4_DIR, title=metadata.title)
        if not filename:
            continue

        logger.debug(" >> Downloaded %s", filename)
        mp3_path = convert_mp4_to_mp3(mp4_path=filename)
        if not mp3_path:
            continue

        metadata.apply_on_file(mp3_path)
        logger.debug(" >> Updated metadata for %s", mp3_path)
