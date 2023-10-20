"""Funtions to extract data from the musicbrainz API, such as an album given a song and a band"""
import logging
import sys
from typing import List, Optional, Tuple

import requests

from config import EMAIL_ADDRESS, IS_DEBUG, TEST_DOWNLOAD_PATH

logger = logging.getLogger("XP3")
logger.setLevel(logging.DEBUG if IS_DEBUG else logging.INFO)


if EMAIL_ADDRESS == "your-mail@mail.com":
    logger.error("Please update your mail address in .env file (MusicBrainz asked to do so")
    sys.exit(1)


def get_track_info(artist: str, title: str) -> List[Tuple[str, int, int]]:
    """Queries musicbrainz.org for candidates (album, year, track number) for the track

    Args:
        artist (str): name of the artist associated with the title
        title (str): name of the title

    Returns:
        List[Tuple[str, int, int]]: list of tuples with possible candidates for album track info
    """
    # MusicBrainz API request URL
    url = f"https://musicbrainz.org/ws/2/recording/?query=artist:{artist} AND recording:{title}&fmt=json"

    # User-Agent header (because they requested nicely)
    headers = {"User-Agent": f"XPrimental/0.0.1 ( {EMAIL_ADDRESS} )"}

    # API request
    response = requests.get(url, headers=headers, timeout=3)
    data = response.json()

    # Extract candidates for: album, year, track
    albums = []
    if "recordings" in data:
        recording_info = data["recordings"]
        logger.debug("Received %d recordings", len(recording_info))
        for recording in recording_info:
            received_title = recording.get("title", "Unknown")
            received_artist = recording.get("artist-credit", [{}])[0].get("artist", {}).get("name", "Unknown")

            if received_title.lower() != title.lower():
                logger.debug("Skipping because of title mismatch (%s != %s)", title, received_title)
                continue

            if received_artist.lower() != artist.lower():
                logger.debug("Skipping because of artist mismatch (%s != %s)", artist, received_artist)
                continue
            logger.debug("Not Skipping. artist: %s, title: %s", received_artist, received_title)
            release_list = recording.get("releases", [])
            logger.debug("Received %d recordings", len(release_list))
            for release in release_list:
                if release.get("title"):
                    album = release.get("title")
                    year = int(release.get("date", "0").split("-")[0]) if release.get("date", "0").split("-")[0] else 0
                    track = int(release.get("media", [{}])[0].get("track-offset", 0)) + 1
                    albums.append((album, year, track))
    return list(set(albums))


def get_release_group_id(artist: str, album: str) -> Optional[str]:
    """Auxilary function to get group_id (used for album art)

    Args:
        artist (str): the artist associated with the album
        album (str): the name of the album

    Returns:
        Optional[str]: the id of the release group, or None in the case of failure
    """
    url = f"https://musicbrainz.org/ws/2/release/?query=artist:{artist} AND release:{album}&fmt=json"
    headers = {"User-Agent": f"XPrimental/0.0.1 ( {EMAIL_ADDRESS} )"}
    try:
        response = requests.get(url, headers=headers, timeout=3)
        response.raise_for_status()
        data = response.json()
        if "releases" in data and data["releases"]:
            release = data["releases"][0]
            if "release-group" in release:
                return release["release-group"]["id"]
        return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def download_album_artwork(artist: str, album: str, filepath: str):
    """Downloads album artwork from coverartarchive.org

    Args:
        artist (str): the artist associated with the album
        album (str): the name of the album
        filepath (str): path for the outputed image file
    """
    release_group_id = get_release_group_id(artist, album)
    url = f"https://coverartarchive.org/release-group/{release_group_id}/front-500"
    headers = {"User-Agent": f"XPrimental/0.0.1 ( {EMAIL_ADDRESS} )"}

    try:
        response = requests.get(url, headers, timeout=3)
        if response.status_code == 200:
            with open(filepath, "wb") as file:
                file.write(response.content)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def main():
    """Just some manual testing, can ignore"""
    artist = "Skillet"
    track = "Dominion"

    track_info = get_track_info(artist, track)
    print(f'Possible album, year, track for "{artist} - {track}":')
    print(track_info)

    while True:
        index = input("Correct choice: ")
        if str.isnumeric(index) and 0 <= int(index) < len(track_info):
            index = int(index)
            break
        print("Invalid choice, choose again")

    download_album_artwork(artist, track_info[index][0], TEST_DOWNLOAD_PATH)


if __name__ == "__main__":
    main()
