"""Funtions to extract data from the musicbrainz API, such as an album given a song and a band"""

import logging
import re
import sys
from collections import Counter
from typing import Any, List, Optional

import requests

from config import EMAIL_ADDRESS, IS_DEBUG, TEST_DOWNLOAD_PATH
from file_operations import save_response_as_json

logging.basicConfig()
logger = logging.getLogger("XP3")
logger.setLevel(logging.DEBUG if IS_DEBUG else logging.INFO)


if EMAIL_ADDRESS == "your-mail@mail.com":
    logger.error("Please update your mail address in .env file (MusicBrainz asked to do so")
    sys.exit(1)

headers = {"User-Agent": f"XPrimental/0.0.1 ( {EMAIL_ADDRESS} )"}


def _perform_generic_get_request(url: str):
    """Performs GET request to a URL

    Args: url (str): The URL to GET

    Returns: A JSON of the response
    """

    # User-Agent header (because they requested nicely)

    # API request
    logger.debug("Sending GET request to %s", url)
    response = requests.get(url, headers=headers, timeout=3)
    data = response.json()
    return data


def _clean_title(title: str) -> str:
    return " ".join(re.sub(r'[\\/:*?"<>|\'’]', "", title).split()).strip().lower()


class ReleaseRecording:
    """Class that represents a recording in MusicBrainz"""

    def __init__(  # pylint: disable=R0917
        self,
        album: str,
        year: int,
        artist: str,
        track: int,
        r_type: str,
        title: str = "",
        status: str = "",
        album_art_path: str = "",
        release_group_id: str = "",
    ) -> None:
        self.album = album
        self.year = year
        self.artist = artist
        self.track = track
        self.type = r_type.lower()
        self.title = title
        self.status = status.lower()
        self.album_art_path = album_art_path
        self.release_group_id = release_group_id

    def __eq__(self, other):
        return (
            self.album == other.album
            and self.year == other.year
            and self.artist == other.artist
            and self.type == other.type
            and self.track == other.track
        )

    def __hash__(self):
        return hash((self.album, self.artist, self.year))

    def __str__(self):
        return f"{self.artist} - {self.album}:{self.track} ({self.year}){' SINGLE' if self.type == 'single' else ''}"

    def __repr__(self):
        return f"{self.artist} - {self.album}:{self.track} ({self.year}){' SINGLE' if self.type == 'single' else ''}"


def get_album_candidates(json_data: Any, artist: str, title: str) -> List[ReleaseRecording]:
    """Given MusicBrainz response, returns album candidates

    Args:
        json_data (Any): Data received from MusicBrainz API
        artist (str): Artist name used for API request
        title (str): Title used for API request

    Returns:
        List[ReleaseRecording]: List of ReleaseRecording with possible candidates for album track info.
    """
    albums = []

    if "recordings" not in json_data:
        return []

    recording_info = json_data["recordings"]
    logger.debug("Received %d recordings", len(recording_info))
    for recording in recording_info:
        received_title = recording.get("title", "Unknown")
        received_artist = recording.get("artist-credit", [{}])[0].get("artist", {}).get("name", "Unknown")

        altered_received_title = _clean_title(received_title)
        altered_title = _clean_title(title)

        # TODO - check if strings are close instead
        if altered_received_title != altered_title:
            logger.debug("Skipping because of title mismatch (%s != %s)", altered_title, altered_received_title)
            continue

        # TODO - check if strings are close instead
        if received_artist.lower() != artist.lower():
            logger.debug("Skipping because of artist mismatch (%s != %s)", artist, received_artist)
            continue
        logger.debug("Not Skipping. artist: %s, title: %s", received_artist, received_title)
        release_list = recording.get("releases", [])
        logger.debug("Received %d releases", len(release_list))
        for release in release_list:
            if not release.get("title"):
                continue

            year = int(release.get("date", "0").split("-")[0]) if release.get("date", "0").split("-")[0] else 0
            release_group = release.get("release-group", {})
            albums.append(
                ReleaseRecording(
                    release.get("title"),
                    year,
                    artist=received_artist,
                    track=int(release.get("media", [{}])[0].get("track-offset", 0)) + 1,
                    r_type=release_group.get("primary-type", ""),
                    title=received_title,
                    status=release.get("status", ""),
                    release_group_id=release_group.get("id", ""),
                )
            )

    # The complication below is to remove duplicates, while giving more weight to albums that appear more
    counter = Counter(albums)
    return sorted(set(albums), key=lambda release: (-counter[release], release.album, release.year, release.track))


def _overwrite_artist_name(json_data: Any, artist_name: str):
    if "recordings" not in json_data:
        return []

    recording_info = json_data["recordings"]
    for recording in recording_info:
        recording["artist-credit"][0]["artist"]["name"] = artist_name


def _get_track_info_fallback(artist: str, title: str) -> List[ReleaseRecording]:
    """Performs a more robust query to musicbrainz.org (in comparison to `get_track_info`).
    Useful for foreign artists, such as Daisuke Ishiwatari which will yield 0 results,
    since his official artist name is 石渡太輔.

    First query for the artist using the wanted alias, and then use the artist ID
    to search for the actual track. Patch the artist name to the wanted alias.

    Args:
        artist (str): name of the artist associated with the title.
        title (str): name of the title.

    Returns:
        List[ReleaseRecording]: List of ReleaseRecording with possible candidates for album track info.
    """
    # MusicBrainz API request URL
    url = f"https://musicbrainz.org/ws/2/artist/?query=artist:{artist}&fmt=json"

    data = _perform_generic_get_request(url)

    artist_id = data["artists"][0]["id"]
    url = f"https://musicbrainz.org/ws/2/recording/?query=arid:{artist_id} AND recording:{title}&fmt=json"

    data = _perform_generic_get_request(url)
    _overwrite_artist_name(data, artist)

    return data


def get_track_info(artist: str, title: str) -> List[ReleaseRecording]:
    """Queries musicbrainz.org for candidates (album, year, track number) for the track.

    Args:
        artist (str): name of the artist associated with the title.
        title (str): name of the title.

    Returns:
        List[ReleaseRecording]: List of ReleaseRecording with possible candidates for album track info.
    """
    # MusicBrainz API request URL
    url = f"https://musicbrainz.org/ws/2/recording/?query=artist:{artist} AND recording:{title}&fmt=json"

    data = _perform_generic_get_request(url)

    # If the response is empty, try a more robust search
    if data["count"] == 0:
        logger.debug("No recordings found - initiating fallback search")
        data = _get_track_info_fallback(artist, title)

    # TODO - if env is dev / prod
    if IS_DEBUG:
        if data.get("created"):
            del data["created"]

        save_response_as_json(data, artist, title)

    # Extract candidates
    return get_album_candidates(data, artist, title)


def get_release_group_id(artist: str, album: str) -> Optional[str]:
    """Auxilary function to get group_id (used for album art)

    Args:
        artist (str): the artist associated with the album
        album (str): the name of the album

    Returns:
        Optional[str]: the id of the release group, or None in the case of failure
    """
    url = f"https://musicbrainz.org/ws/2/release/?query=artist:{artist} AND release:{album}&fmt=json"
    try:
        logger.debug("Sending GET request to %s", url)
        response = requests.get(url, headers=headers, timeout=3)
        response.raise_for_status()
        data = response.json()
        if "releases" in data and data["releases"]:
            releases = data["releases"]
            for release in releases:
                if "release-group" in release and album.lower() == release["release-group"]["title"].lower():
                    logger.debug(" > Found release group")
                    return release["release-group"]["id"]

        logger.debug(" > Haven't found release group")
        return None
    except requests.exceptions.RequestException as err:
        logger.error("An error occurred: %s", err)
        return None


def download_album_artwork_from_release_id(release_group_id: str, filepath: str):
    """Downloads album artwork from coverartarchive.org, given a release group id

    Args:
        release_group_id (str): the id of the release group
        filepath (str): path for the outputed image file
    """
    url = f"https://coverartarchive.org/release-group/{release_group_id}/front-500"

    try:
        logger.debug("Sending GET request to %s", url)
        response = requests.get(url, headers, timeout=3)
        if response.status_code == 200:
            with open(filepath, "wb") as file:
                file.write(response.content)
    except requests.exceptions.RequestException as err:
        logger.error("An error occurred: %s", err)


def download_album_artwork(artist: str, album: str, filepath: str):
    """Downloads album artwork from coverartarchive.org

    Args:
        artist (str): the artist associated with the album
        album (str): the name of the album
        filepath (str): path for the outputed image file
    """
    release_group_id = get_release_group_id(artist, album)
    print(release_group_id)
    if release_group_id is None:
        logger.debug("Couldn't find release group for '%s - %s', aborting album art download", artist, album)
        return

    download_album_artwork_from_release_id(release_group_id, filepath)


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

    download_album_artwork_from_release_id(track_info[index].release_group_id, TEST_DOWNLOAD_PATH)


if __name__ == "__main__":
    main()
