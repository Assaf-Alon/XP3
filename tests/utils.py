"""Utilities used for testing"""

import hashlib
import os
import re
import shutil

from config import TMP_DIR
from file_operations import load_json_response


def get_file_md5_hash(filepath: str) -> str:
    """Gets the md5 hash of a file

    Args:
        filepath (str): The path of the file

    Returns:
        str: The md5 hash of the file
    """
    with open(filepath, "rb") as file:
        data = file.read()
        file_md5 = hashlib.md5(data, usedforsecurity=False).hexdigest()
    return file_md5


def mock_artwork_downloader(artist: str, album: str):
    """Fakes the process of downloading an album image for a given artist and album"""
    dirname = os.path.dirname(__file__)
    png_path = os.path.join(dirname, "outputs", "img", f"{artist} - {album}.png")
    target_path = os.path.join(TMP_DIR, f"{artist} - {album}.png")
    shutil.copyfile(src=png_path, dst=target_path)


def mocked_requests_get(*args, **kwargs):
    """Used for testing to avoid API calls"""

    class MockResponse:
        """Mocked class of a json response"""

        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            """json..."""
            return self.json_data

    url = args[0]
    url_match = re.match(r".*artist:(?P<artist>.+) AND recording:(?P<title>.*)&fmt=json", url)

    if url_match:
        artist = url_match.group("artist")
        title = url_match.group("title")

        data = load_json_response(artist, title)
        return MockResponse(data, 200)

    # https://coverartarchive.org/release-group/46303229-3ef4-480d-b648-a78e1c64c911/front-500
    url_match = re.match(r".*release-group/(?P<release_group_id>.+)/.+", url)

    if url_match:
        return MockResponse({}, 200)
        # TODO - Something about this?
        # release_group = url_match.group("release_group_id")
        # load_json_response(release_group)

    if not url_match:
        raise ValueError(f"URL not in the right format: {url}")

    artist = url_match.group("artist")
    title = url_match.group("title")

    data = load_json_response(artist, title)
    return MockResponse(data, 200)
