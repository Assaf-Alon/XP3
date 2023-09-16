import pytube
from moviepy.editor import VideoFileClip

from mp3_metadata import MP3MetaData
from constants import MP3_DIR, MP4_DIR, DEFAULT_PLAYLIST, IS_DEBUG

from os.path import join, basename

import logging
from typing import Optional, Tuple, List

logger = logging.getLogger("XP3")
logger.setLevel(logging.DEBUG if IS_DEBUG else logging.INFO)


def get_playlist_songs(
    playlist_url: str = DEFAULT_PLAYLIST,
    start_index: int = 0,
    end_index: int = 999999,
    interactive: bool = True,
    update_album: bool = True,
) -> List[Tuple[MP3MetaData, str]]:

    playlist = pytube.Playlist(playlist_url)

    logger.debug(f"Number of videos in playlist: {len(playlist.video_urls)}")
    start_index -= 1
    end_index = min(end_index - 1, len(playlist.video_urls))

    songs = []
    videos = list(playlist.videos)
    for index in range(start_index, end_index + 1):
        py_video = videos[index]
        metadata = MP3MetaData.from_video(
            title=py_video.title, channel=py_video.author, interactive=interactive
        )
        if update_album:
            metadata.update_missing_fields(interactive=interactive)
            metadata.update_album_art()
        songs.append((metadata, py_video.watch_url))

    return songs


def download_ytvid(video_url: str, out_path: str = MP4_DIR, title: Optional[str] = None) -> Optional[str]:
    if title and not title.endswith(".mp4"):
        title = title + ".mp4"
    mp4_stream = pytube.YouTube(video_url).streams.filter(file_extension="mp4").first()
    if not mp4_stream:
        logger.error(f"No stream found for {video_url}")
        return 
    return mp4_stream.download(output_path=out_path, filename=title)



def convert_mp4_to_mp3(mp4_path: str) -> Optional[str]:
    assert mp4_path.endswith(".mp4")
    mp4_filename = basename(mp4_path)
    mp3_path = join(MP3_DIR, mp4_filename[:-1] + "3")
    video = VideoFileClip(mp4_path)
    if not video.audio:
        logger.error(f"Audio not found for {mp4_path}")
        return
    video.audio.write_audiofile(mp3_path)
    return mp3_path


def download_XPrimental(
    playlist_url: str = DEFAULT_PLAYLIST,
    start_index: int = 0,
    end_index: int = 99999,
    interactive: bool = True,
):
    songs = get_playlist_songs(
        playlist_url=playlist_url, start_index=start_index, end_index=end_index
    )
    for metadata, url in songs:
        logger.debug(f" > Downloading {metadata.title}, from {url}")
        filename = download_ytvid(url, out_path=MP4_DIR, title=metadata.title)
        if not filename:
            continue
        
        logger.debug(f" >> Downloaded {filename}")
        mp3_path = convert_mp4_to_mp3(mp4_path=filename)
        if not mp3_path:
            continue

        metadata.apply_on_file(mp3_path)
        logger.debug(f" >> Updated metadata for {mp3_path}")
