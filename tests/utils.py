"""Utilities used for testing"""
import hashlib
import json
import os
import shutil
from typing import List

from config import TMP_DIR
from music_api import ReleaseRecording, get_album_candidates


def get_file_md5_hash(filepath: str) -> str:
    """Gets the md5 hash of a file

    Args:
        filepath (str): The path of the file

    Returns:
        str: The md5 hash of the file
    """
    with open(filepath, "rb") as file:
        data = file.read()
        file_md5 = hashlib.md5(data).hexdigest()
    return file_md5


def mock_rise_against_artwork_downloader(band: str = "", name_for_art: str = "", filepath: str = ""):
    dirname = os.path.dirname(__file__)
    png_path = os.path.join(dirname, "outputs", "img", "Rise Against - Appeal to Reason.png")
    target_path = os.path.join(TMP_DIR, "Rise Against - Appeal to Reason.png")
    shutil.copyfile(src=png_path, dst=target_path)


def mock_get_track_info(artist: str, title: str) -> List[ReleaseRecording]:
    """
    Mock function of music_api.get_track_info that loads json from local path
    instead of getting it from the MusicBrainz API
    """
    dirname = os.path.dirname(__file__)
    json_path = os.path.join(dirname, "outputs", "json", f"{artist} - {title}.json")
    data = json.load(json_path)

    # Extract candidates
    return get_album_candidates(data, artist, title)
