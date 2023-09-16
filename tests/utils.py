import hashlib


def get_file_md5_hash(filepath: str) -> str:
    with open(filepath, "rb") as file:
        data = file.read()
        file_md5 = hashlib.md5(data).hexdigest()
    return file_md5
