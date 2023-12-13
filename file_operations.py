"""Handles file operations, such as naming, downloading and loading"""


import json
import os
import re
from os.path import join
from typing import Tuple

from config import IMG_DIR, PATTERN_ILLEGAL_CHARS


def save_response_as_json(data: dict, artist: str, title: str):
    """Saves a response from MusicBrainz API to a json file.

    Args:
        data (dict): The data itself.
        artist (str): The artist name that was used in the request.
        title (str): The title that was used in the request.
    """
    dirname = dirname = os.path.dirname(__file__)
    filename = f"{artist} - {title}.json".lower().replace("*", "_").replace("/", "_").replace("\\", "_")
    json_path = os.path.join(dirname, "tests", "outputs", "json", filename)
    with open(json_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file)


def load_json_response(artist: str, title: str) -> dict:
    """Loads a saved response associated with a given artist and title

    Returns: The saved data associated with the given artist and title.
    """
    dirname = dirname = os.path.dirname(__file__)
    filename = f"{artist} - {title}.json".lower().replace("*", "_").replace("/", "_").replace("\\", "_")
    json_path = os.path.join(dirname, "tests", "outputs", "json", filename)
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.loads(file.read())
    return data


def get_album_artwork_path(band: str, song: str, album: str = "") -> Tuple[str, str]:
    """Gets path for the album artwork image.
    If it exists, the album will be used. Otherwise, the song will be used.

    Returns:
        Tuple[str, str]: First element is the path. Second element is the album, or song if there's no album.
    """
    name_for_art = album if album else song

    # Remove illegal characters
    name_for_art = " ".join(re.sub(PATTERN_ILLEGAL_CHARS, "_", name_for_art).split()).strip()
    album_artwork_path = join(IMG_DIR, f"{band} - {name_for_art}.png")
    return album_artwork_path, name_for_art
