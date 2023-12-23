"""Module providing a class to work with mp3 metadata (MP3MetaData) and related utilities"""
import datetime
import logging
import os
import re
import sys
from os.path import basename, dirname, isfile
from pathlib import Path
from typing import List, Optional, Tuple

import music_tag
from colorama import Back, Fore
from dateutil import parser
from dateutil.parser import ParserError

from config import IS_DEBUG, PATTERN_ILLEGAL_CHARS
from file_operations import get_album_artwork_path
from music_api import (
    ReleaseRecording,
    download_album_artwork,
    download_album_artwork_from_release_id,
    get_track_info,
)
from user_interaction import choose_recording, get_user_input, print_suggestions


class MP3MetaData:
    """Forward declaration of class so that relevant functions will be able to use it"""

    pass  # pylint: disable=unnecessary-pass


logging.basicConfig()
logger = logging.getLogger("XP3")
logger.setLevel(logging.DEBUG if IS_DEBUG else logging.INFO)


STRINGS_TO_REMOVE = ["with Lyrics", "Lyrics", "720p", "1080p", "Video", "LYRICS"]


def extract_date_from_string(string: str) -> Optional[datetime.datetime]:
    """Returns a date written in a string if exists. Otherwise returns None."""
    try:
        date = parser.parse(string, fuzzy=True)
        return date
    except ParserError:
        return None


# TODO - Handle DECO here
# TODO - Function is too long, split to smaller ones
def get_title_suggestion(
    title: str = "", band: str = "", song: str = "", channel="", interactive=False
) -> Tuple[str, str]:
    """Gets a suggested artist and track name, given a (possibly bad) title / band and song
    If `band` and `song` aren't provided, title must be provided.
    Args:
        title (str, optional): The full title (e.g. `Linkin Park - Papercut`). Defaults to "".
        band (str, optional): The band in question. Defaults to "".
        song (str, optional): The song in question. Defaults to "".
        channel (str, optional): Name of channel (used if song was taken from an external source). Defaults to "".
        interactive (bool, optional): Whether user can give interactive feedback to the suggestion. Defaults to False.

    Returns:
        Tuple[str, str]: Suggested band and suggested song
    """
    assert (band and song) or title

    if band and song:
        title = band + " - " + song

    suggested_title = title

    # Swap colon (:) with hyphen (-)
    if "-" not in suggested_title and ":" in suggested_title:
        suggested_title = suggested_title.replace(":", "-")

    # Remove illegal characters
    suggested_title = " ".join(re.sub(PATTERN_ILLEGAL_CHARS, "", suggested_title).split()).strip()

    # Remove parentheses (and content)
    pattern1 = r"\([^)]*\)"
    pattern2 = r"\[[^]]*\]"
    suggested_title = " ".join(re.sub(pattern1, "", suggested_title).split()).strip()
    suggested_title = " ".join(re.sub(pattern2, "", suggested_title).split()).strip()

    # Dash whitespace
    if suggested_title.find("-") >= 0:
        pattern3 = r"\s?-\s?"
        suggested_title = " ".join(re.sub(pattern3, " - ", suggested_title).split()).strip()

    # Attempt to patch with channel name if possible
    elif channel:
        channel = channel.replace(" - Topic", "")
        suggested_title = channel + " - " + suggested_title

    for s in STRINGS_TO_REMOVE:
        suggested_title = suggested_title.replace(s, "")
    suggested_title = suggested_title.strip()

    should_update_title = True
    if interactive and suggested_title != title:
        print("\n------------------------------")
        print("About to update title of song.")
        print(f"Original  title: {title}")
        print("Suggested title: " + Fore.BLUE + Back.WHITE + suggested_title + Fore.RESET + Back.RESET)

        # Extra variable for linter
        should_use_suggestion_input = get_user_input("Should use suggestion?", True)
        assert isinstance(should_use_suggestion_input, bool)
        should_update_title = should_use_suggestion_input

    # Don't use suggestion, type manually
    if should_update_title is False:
        # Extra variable for linter
        title_from_user = get_user_input("Enter the name of the title manually", title)
        assert isinstance(title_from_user, str)
        suggested_title = title_from_user

    # Update fields
    title = suggested_title
    if suggested_title.count(" - ") == 1:
        band, song = suggested_title.split(" - ")
    elif suggested_title.count(" - ") >= 1:
        band, *rest = suggested_title.split(" - ")
        song = " - ".join(rest)
    else:
        band, song = "", ""

    band = band.strip()
    song = song.strip()
    return band, song


def get_title_from_path(file_path: str) -> str:
    """Gets title from the name of the file, giving the file's full path

    Args:
        file_path (str): Path of the file.

    Returns:
        str: File name without extension.
    """
    file_name = basename(file_path)
    assert file_name.endswith(".mp3")
    file_name_no_extension = file_name[:-4]
    return file_name_no_extension


def get_suggested_recording_from_partial_metadata(
    recordings: List[ReleaseRecording], partial_metadata: MP3MetaData
) -> int:
    """
    Auxiliary function for get_suggested_recording.
    Tries to filter recordings for only relevant albums from partial metadata
    Returns:
        int: the index of the recording, or -1 if haven't found a decent match
    """
    logger.debug("Attempting to filter suggested from partial metadata")
    valid_recording_indexes = range(0, len(recordings))
    if len(valid_recording_indexes) == 1:
        return 0
    if partial_metadata.year:
        valid_recording_indexes = [
            index for index in valid_recording_indexes if recordings[index].year == partial_metadata.year
        ]

    if partial_metadata.album:
        valid_recording_indexes = [
            index for index in valid_recording_indexes if recordings[index].album == partial_metadata.album
        ]

    if partial_metadata.album:
        valid_recording_indexes = [
            index for index in valid_recording_indexes if recordings[index].album == partial_metadata.album
        ]

    if partial_metadata.track:
        valid_recording_indexes = [
            index for index in valid_recording_indexes if recordings[index].track == partial_metadata.track
        ]

    # TODO - can possibly improve this by calling get_suggested_recording with valid indexes if its length is >= 1
    if len(valid_recording_indexes) == 1:
        logger.debug(
            "Found only 1 recording that matches the partial metadata - %s", recordings[valid_recording_indexes[0]]
        )
        return valid_recording_indexes[0]

    return -1


def should_skip_recording(recording: ReleaseRecording) -> bool:
    """
    Returns true if and only if shouls skip the recording,
    decision is based on basic heuristics
    """
    if recording.year == 0:
        logger.debug("Skipping %s because year == 0", recording.album)
        return True
    if "hits" in recording.album.lower():
        logger.debug("Skipping %s because it contains hits", recording.album)
        return True
    if "live" in recording.album.lower():
        logger.debug("Skipping %s because it contains live", recording.album)
        return True
    if "best" in recording.album.lower():
        logger.debug("Skipping %s because it contains best", recording.album)
        return True

    date_from_album = extract_date_from_string(recording.album.lower())
    if date_from_album:
        logger.debug(
            "Skipping %s because it contains date: %s",
            recording.album,
            str(date_from_album),
        )
        return True
    if "promotion" in recording.status:
        logger.debug("Skipping %s because the status is promotional", recording.album)
        return True

    return False


def get_suggested_recording(recordings: List[ReleaseRecording], partial_metadata: Optional[MP3MetaData] = None) -> int:
    """Returns the index of a likely correct recording out of the recordings list using heurestics.

    Args:
        recordings (List[ReleaseRecording]): A sorted list (by year) of recordings to get suggestion from.
        partial_metadata (MP3MetaData, optional): Partial metadata. For example, contains only album name.

    Returns:
        int: Index of suggested recording, or -1 if there's no suggestion
    """
    # TODO - Instead of linear scan, run 'min' with a function, give score according to heuristics
    # e.g., year > 0 is worth 1000 points
    #       title contains forbidden works (hits, best), negative 200 points
    #       single, negative 10 points

    # Try to find an album that fits the existing partial metadata
    if partial_metadata:
        suggested_recording_index = get_suggested_recording_from_partial_metadata(recordings, partial_metadata)
        if suggested_recording_index >= 0:
            return suggested_recording_index

    suggested_recording_index = -1
    potential_single_index = -1
    for recording_index, recording in enumerate(recordings):
        if should_skip_recording(recording):
            continue

        if recording.type in ("single", "ep"):
            logger.debug("Skipping %s because it's single/ep", recording.album)
            if potential_single_index == -1:
                logger.debug("But remembering it in case there's no good album")
                potential_single_index = recording_index
            continue
        # It's not uncommon for a song to be released as a single, labeled as album for some reason,
        # and later that year to be released in a proper album.
        # if (
        #     recording.title.lower() in recording.album.lower()
        #     and recording_index + 1 < len(recordings)
        #     and recordings[recording_index + 1].year == recording.year
        # ):
        #     continue

        if recording.year > 0:
            # Large gap between single and album release, likely that it's more well known as a single
            if potential_single_index >= 0 and recording.year - recordings[potential_single_index].year >= 2:
                suggested_recording_index = potential_single_index
            else:
                suggested_recording_index = recording_index
            break
    return suggested_recording_index if suggested_recording_index >= 0 else potential_single_index


class MP3MetaData:  # pylint: disable=E0102
    """Class that represents mp3 metadata."""

    def __init__(
        self,
        band: str,
        song: str,
        album: str = "",
        year: int = 0,
        track: int = 0,
        genre: str = "",
        art_path: str = "",
        art_configured: bool = False,
        release_group_id: str = "",
    ):
        self.band = band
        self.song = song
        self.album = album
        self.year = year
        self.track = track
        self.genre = genre
        self.art_path = art_path
        self.art_configured = art_configured
        self.release_group_id = release_group_id

    @staticmethod
    def mp3_file_get_as_str(mp3_file: dict, key: str) -> str:
        """type checker on dict for mp3_file library"""
        value = mp3_file.get(key)
        if value is None or not hasattr(value, "value"):
            return ""

        return str(value.value)

    @classmethod
    def from_file(cls, file_path: str, interactive: bool = False, extract_image: bool = False):
        """Initalized an instance of the class from a file and its metadata.

        Args:
            file_path (str): The path of the file.
            interactive (bool, optional): Whether can use user input to decide on names. Defaults to False.
            extract_image (bool, optional): If image already exists, save it as a file. Defaults to False.

        Returns:
            MP3MetaData: Instance of the class from the file.
        """
        assert file_path.endswith(".mp3")
        assert isfile(file_path)

        try:
            mp3_file = music_tag.load_file(file_path)
        except Exception:  # pylint: disable=broad-exception-caught
            mp3_file = dict()

        album_artwork_path = ""
        if not mp3_file or mp3_file is None:
            song, band, album, year, track, album_art, art_configured = (
                "",
                "",
                "",
                0,
                0,
                "",
                False,
            )
        else:
            song = cls.mp3_file_get_as_str(mp3_file, "title").strip()
            band = cls.mp3_file_get_as_str(mp3_file, "artist").strip()
            album = cls.mp3_file_get_as_str(mp3_file, "album").strip()
            year = int(cls.mp3_file_get_as_str(mp3_file, "year"))
            track = int(cls.mp3_file_get_as_str(mp3_file, "tracknumber"))

            try:
                album_art = mp3_file.get("artwork")
            except Exception:
                album_art = None
            art_configured = bool(album_art)

        # Patch band and song
        if not (song and band):
            title = get_title_from_path(file_path)
            band, song = get_title_suggestion(title, interactive=interactive)

        # Attempt patching album and year
        if not (album and year):
            album_info = MP3MetaData.extract_album_info_from_path(file_path)
            if album_info is not None:
                album = album_info[1]
                year = album_info[2]

        # Attempt patching album art
        if album_art:
            album_artwork_path, _ = get_album_artwork_path(band, song, album)

            # Extract image if it's not in the IMG DIR
            if extract_image and not isfile(album_artwork_path) and isinstance(album_art, music_tag.file.MetadataItem):
                album_art.value.image.save(fp=album_artwork_path)

        return cls(
            band=band,
            song=song,
            album=album,
            year=year,
            track=track,
            art_path=album_artwork_path,
            art_configured=art_configured,
        )

    @classmethod
    def from_title(cls, title: str, interactive: bool = False):
        """Initalized an instance of the class from a title.

        Args:
            title (str): The title.
            interactive (bool, optional): Whether can use user input to decide on names. Defaults to False.

        Returns:
            MP3MetaData: Instance of the class from the title.
        """
        band, song = get_title_suggestion(title=title, interactive=interactive)
        return cls(band=band, song=song)

    @classmethod
    def from_video(cls, title: str, channel: str = "", interactive: bool = False):
        """Initalized an instance of the class from a video (title and hosting channel).

        Args:
            title (str): The title.
            channel (str, optional): The hosting channel. Defaults to "".
            interactive (bool, optional): Whether can use user input to decide on names. Defaults to False.

        Returns:
            MP3MetaData: Instance of the class from the title.
        """
        band, song = get_title_suggestion(title=title, channel=channel, interactive=interactive)
        return cls(band=band, song=song)

    @staticmethod
    def extract_album_info_from_path(file_path: str) -> Optional[Tuple[str, str, int]]:
        """Tries to get album info from a path to a file.
           Uses the convention that album directory names are `ALBUM (YEAR)`

        Args:
            file_path (str): The path to the file

        Returns:
            Optional[Tuple[str, str, int]]: (<artist>, <album>, <year>)
        """
        parent_directory_path = dirname(file_path)
        parent_directory = basename(parent_directory_path)
        # No album info if directory's pattern is not `ALBUM (YEAR)``
        path_match = re.match(r"(?P<album>.+) \((?P<year>\d{4})\)", parent_directory)
        if not path_match:
            return None

        grandparent_directory = basename(dirname(parent_directory))
        return (
            grandparent_directory,
            path_match.group("album"),
            int(path_match.group("year")),
        )

    @property
    def title(self) -> str:
        """Get title (band - song)"""
        return self.band + " - " + self.song

    def update_fields_from_recording(self, recording: Optional[ReleaseRecording] = None, full_update: bool = True):
        """
        If recording is given, updates year, album, track from it.
        If full_update is set to False, the band and song names aren't updated from the recording
        """
        if not recording:
            return
        self.year = recording.year
        self.album = recording.album
        self.track = recording.track
        self.release_group_id = recording.release_group_id
        
        if full_update:
            self.band = recording.artist
            self.song = recording.title


    def update_missing_fields(self, interactive: bool = False, keep_current_metadata: bool = False):
        """Updates missing mp3 metadata fields.
        Args:
            interactive (bool, optional): Should run in interactive mode, get user feedback regarding title fixes.
                                          Defaults to False.
            keep_current_metadata (bool, optional): States whether to use existing metadata.
                                                    Defaults to False.
        """
        if not self.title:
            logger.debug("No title. Returning...")
            return

        # Check if there're missing fields
        if self.album and self.year and self.track:
            # Not interactive and keeping metadata, nothing to do
            if not interactive and keep_current_metadata:
                logger.debug("Keeping current metadata for %s", self.title)
                return
            if not interactive or keep_current_metadata:
                should_use_existing_metadata = keep_current_metadata
            else:  # Interactive mode, keep_current_metadata is False
                interactive_keep_current_metadata = get_user_input(
                    prompt=f"""Metadata already set.
{self.title}
album = {self.album}
year = {self.year}
track = {self.track}
Skip?""",
                    default=True,
                )
                assert isinstance(interactive_keep_current_metadata, bool)
                should_use_existing_metadata = interactive_keep_current_metadata

            if should_use_existing_metadata:
                return

        # Get recording candidates
        artist, title = self.band, self.song
        recordings = get_track_info(artist, title)

        # Sort by release year (main), and by length of album (secondary)
        recordings.sort(key=lambda recording: (recording.year, len(recording.album)))

        suggested_album_index = get_suggested_recording(recordings, self)

        if not interactive:
            if not recordings:
                return
            suggested_album_index = max(suggested_album_index, 0)
            self.update_fields_from_recording(recordings[suggested_album_index])
            return
        print_suggestions(recordings, artist, title, suggested_album_index)
        chosen_recording = choose_recording(recordings, suggested_album_index, title)
        if chosen_recording is not None:
            self.update_fields_from_recording(chosen_recording)

        logger.debug("Album: %s, year: %d, track: %d", self.album, self.year, self.track)

    def update_album_art(self, album_artwork_path: Optional[str] = None, force_download: bool = False):
        """
        Updates album artwork path. Downloads the artwork if necessary.
        The album_artwork_path is infered from the artist and song/album, unless provided explicitly.
        The default path is <IMG DIR>/<artist> - <album/song>.png
        Args:
            album_artwork_path (str, optional): The path of the album artwork. Defaults to None.
            force_download (bool, optional): Download the album artwork even if it exists. Defaults to False.
        """
        logger.debug("[update_album_art] Called with album name %s.", self.album)
        if not self.band:
            logger.debug("[update_album_art] no band, returning")
            return

        if not (self.album or self.song):
            logger.debug("[update_album_art] no album and no song, returning")
            return
        if album_artwork_path is None:
            album_artwork_path, name_for_art = get_album_artwork_path(self.band, self.song, self.album)
            logger.debug("Generated album artwork path: %s. Name for art: %s", album_artwork_path, name_for_art)

        if not isfile(album_artwork_path) or force_download:
            if not isfile(album_artwork_path):
                logger.debug("Album art %s not found. downloading", album_artwork_path)
            if force_download:
                logger.debug("Force downloading %s", album_artwork_path)

            if hasattr(self, "release_group_id") and self.release_group_id:
                download_album_artwork_from_release_id(self.release_group_id, album_artwork_path)
            elif name_for_art:
                download_album_artwork(self.band, name_for_art, filepath=album_artwork_path)
            else:
                logger.error("Song doesn't have release group id and failed to get name for art")

        # Make sure the file does exist (in case the download has failed)
        if isfile(album_artwork_path):
            self.art_path = album_artwork_path

    def apply_on_file(self, file_path: str):
        """Applies metadata on a file - updates metadata fields according to the class attributes

        Args:
            file_path (str): The path to the file
        """
        if not isfile(file_path):
            logger.error("File not found: %s", file_path)
            return

        mp3_file = music_tag.load_file(file_path)
        if not mp3_file:
            logger.error("Failed to load %s", file_path)
            return

        # For linter
        assert isinstance(mp3_file, music_tag.id3.Mp3File)

        if self.song:
            mp3_file["title"] = self.song

        if self.band:
            mp3_file["artist"] = self.band
            mp3_file["albumartist"] = self.band

        if self.year:
            mp3_file["year"] = self.year

        if self.album:
            mp3_file["album"] = self.album

        if self.track:
            mp3_file["tracknumber"] = self.track

        if self.art_path:
            with open(self.art_path, "rb") as img:
                mp3_file["artwork"] = img.read()
                logger.debug("Updated album artwork from %s", self.art_path)

        mp3_file.save()

    def __repr__(self):
        if self.song and self.band:
            return self.band + " - " + self.song
        return "Bad song"

    def __str__(self):
        if self.song and self.band:
            return self.band + " - " + self.song
        return "Bad song"


# TODO - use this to load metadata if exists, and process song name (DECO)


def update_metadata_for_directory(
    base_path: str,
    interactive: bool = True,
    update_album_art: bool = False,
    recursive: bool = False,
    force_download_album_art: bool = False,
    keep_current_metadata: bool = False,
):
    """Updates mp3 metadata of files in a directory.

    Args:
        base_path (str): Path of the directory that contains the mp3 files
        interactive (bool, optional): Should run in interactive mode. Defaults to True.
        update_album_art (bool, optional): Should update the album art of the files. Defaults to False.
        recursive (bool, optional): Should apply to subdirectories. Defaults to False.
        force_download_album_art (bool, optional): Downloads album art even if already exists. Defaults to False.
                                                   Relevant only if `update_album_art` is set to True
        keep_current_metadata (bool, optional): Doesn't overwrite metadata if exists. Defaults to False
    """
    if not os.path.isdir(base_path):
        logger.error("Provided base path %s is not an existing directory", base_path)
        sys.exit(1)

    paths = Path(base_path).rglob("*.mp3") if recursive else Path(base_path).glob("*.mp3")

    for path in paths:
        update_metadata_for_file(
            str(path.absolute()), interactive, keep_current_metadata, update_album_art, force_download_album_art
        )


def update_metadata_for_file(
    file_path: str,
    interactive: bool = False,
    keep_current_metadata: bool = False,
    update_album_art: bool = False,
    force_download_album_art: bool = False,
):
    """
    Updates metadata for a single file.
    Intended to run on file that has full metadata fields set, with the only exception being the album art
    """
    logger.debug("Getting metadata from %s", file_path)
    metadata = MP3MetaData.from_file(file_path, interactive)
    metadata.update_missing_fields(interactive, keep_current_metadata)
    if update_album_art:
        metadata.update_album_art(force_download=force_download_album_art)
        logger.debug("Album art path: %s", metadata.art_path)
    metadata.apply_on_file(file_path)


def update_image_for_file(file_path: str, interactive: bool = False):
    """
    Updates an image for a file.
    Intended to run on file that has full metadata fields set, with the only exception being the album art
    """
    metadata = MP3MetaData.from_file(file_path, interactive)
    metadata.update_album_art()
    metadata.apply_on_file(file_path)
