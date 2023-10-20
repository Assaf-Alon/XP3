"""Utilities used for testing"""
import hashlib


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
