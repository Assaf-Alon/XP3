"""Definitions of variables used for configurations, such as directory paths"""
from decouple import config

EMAIL_ADDRESS = str(config("EMAIL_ADDRESS", default="alon.assaf@campus.technion.ac.il", cast=str))
TEST_DOWNLOAD_PATH = str(config("TEST_DOWNLOAD_PATH", default="C:\\Temp\\DOMinion.png", cast=str))
IS_DEBUG = config("DEBUG", default=False)


MP3_DIR = str(config("MP3_DIR", cast=str))
MP4_DIR = str(config("MP4_DIR", cast=str))
IMG_DIR = str(config("IMG_DIR", cast=str))
TMP_DIR = str(config("TMP_DIR", cast=str))
DEFAULT_PLAYLIST = str(
    config(
        "DEFAULT_PLAYLIST", cast=str, default="https://www.youtube.com/playlist?list=PLofmCZWRdOtl1dM2XQPx2_8KxveP6KbTt"
    )
)
