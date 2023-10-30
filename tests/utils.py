"""Utilities used for testing"""
import hashlib
import os
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
