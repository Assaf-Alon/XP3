"""Utilities used for testing"""
import hashlib
import json
import os
import re
import shutil

from config import TMP_DIR


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


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    url = args[0]
    url_match = re.match(r".*artist:(?P<artist>.+) AND recording:(?P<title>.*)&fmt=json", url)

    if not url_match:
        raise ValueError(f"URL not in the right format: {url}")

    artist = url_match.group("artist")
    title = url_match.group("title")

    dirname = os.path.dirname(__file__)
    json_path = os.path.join(dirname, "outputs", "json", f"{artist} - {title}.json")
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.loads(file.read())
    return MockResponse(data, 200)
