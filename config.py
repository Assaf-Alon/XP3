"""Definitions of variables used for configurations, such as directory paths"""
import sys
from os.path import expanduser, join
from pathlib import Path

from decouple import config

home = expanduser("~")

EMAIL_ADDRESS = str(config("EMAIL_ADDRESS", default="alon.assaf@campus.technion.ac.il", cast=str))
TEST_DOWNLOAD_PATH = str(config("TEST_DOWNLOAD_PATH", default="C:\\Temp\\DOMinion.png", cast=str))
IS_DEBUG = config("DEBUG", default=False)


MP3_DIR = str(config("MP3_DIR", cast=str, default=join(home, "mp3")))
MP4_DIR = str(config("MP4_DIR", cast=str, default=join(home, "mp4")))
IMG_DIR = str(config("IMG_DIR", cast=str, default=join(home, "img")))
TMP_DIR = str(config("TMP_DIR", cast=str, default=join(home, "tmp")))

XP3_DIRS = (MP3_DIR, MP4_DIR, IMG_DIR, TMP_DIR)

DEFAULT_PLAYLIST = str(
    config(
        "DEFAULT_PLAYLIST", cast=str, default="https://www.youtube.com/playlist?list=PLofmCZWRdOtl1dM2XQPx2_8KxveP6KbTt"
    )
)


for directory in XP3_DIRS:
    dir_path = Path(directory)
    try:
        dir_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Failed to create {directory} directory: {e}")
        sys.exit(1)
