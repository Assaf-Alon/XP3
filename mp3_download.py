"""Functions used to get data related to mp3 files and download them"""

import logging
from os.path import join
from typing import List, Optional, Tuple

import yt_dlp as youtube_dl

from config import DEFAULT_PLAYLIST, IS_DEBUG, MP3_DIR
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
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        playlist_dict = ydl.extract_info(playlist_url, download=False)

    logger.debug("Number of videos in playlist: %d", len(playlist_dict["entries"]))
    start_index -= 1
    end_index = min(end_index, len(playlist_dict["entries"])) - 1
    logger.debug("Start: %d, End: %d", start_index, end_index)

    songs = []
    for index in range(start_index, end_index + 1):
        logger.debug(" > Processing song (%d/%d)", index, end_index)
        entry = playlist_dict["entries"][index]
        metadata = MP3MetaData.from_video(title=entry["title"], channel=entry["uploader"], interactive=interactive)
        if update_album:
            metadata.update_missing_fields(interactive=interactive)
            metadata.update_album_art()
        songs.append((metadata, entry["url"]))

    return songs


def download_song(
    song_url: str,
    out_path: str = MP3_DIR,
    metadata: Optional[MP3MetaData] = None,
    update_album: bool = True,
    interactive: bool = True,
) -> Optional[str]:
    """Downloads a single song and updates its metadata

    Args:
        song_url (str): The URL of the song
        out_path (str, optional): The directory to save the downloaded song. Defaults to MP3_DIR.
        metadata (MP3MetaData, optional): The metadata of the song. Defaults to None.
        update_album (bool, optional): Whether to update album metadata or not. Defaults to True.
        interactive (bool, optional): Whether to run metadata updates in interactive mode. Defaults to True.

    Returns:
        Optional[str]: Path to the downloaded mp3 file.
    """
    title = metadata.title
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": (
            join(out_path, f"{title}.%(ext)s") if title else join(out_path, "%(title)s.%(ext)s")
        ),  # %(title) is the video title, as described in https://github.com/ytdl-org/youtube-dl#output-template
        "quiet": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(song_url, download=True)
    mp3_path = join(out_path, f"{title}.mp3") if title else join(out_path, f"{info_dict['title']}.mp3")
    if metadata is None:
        metadata = MP3MetaData.from_video(
            title=info_dict["title"], channel=info_dict["uploader"], interactive=interactive
        )
    if update_album:
        metadata.update_missing_fields(interactive=interactive)
        metadata.update_album_art()
    metadata.apply_on_file(mp3_path)
    logger.debug(" >> Updated metadata for %s", mp3_path)
    return mp3_path


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
        download_song(url, out_path=MP3_DIR, metadata=metadata, update_album=True, interactive=interactive)
