"""Module providing a class to work with mp3 metadata (MP3MetaData) and related utilities"""
import datetime
import logging
import os
import re
import sys
from os.path import basename, dirname, isfile, join
from pathlib import Path
from typing import Any, List, Optional, Tuple

import music_tag
from colorama import Back, Fore
from dateutil import parser
from dateutil.parser import ParserError

from config import IMG_DIR, IS_DEBUG
from music_api import ReleaseRecording, download_album_artwork, get_track_info

logger = logging.getLogger("XP3")
logger.setLevel(logging.DEBUG if IS_DEBUG else logging.INFO)

PATTERN_ILLEGAL_CHARS = r'[\\/:*?"<>|]'
STRINGS_TO_REMOVE = ["with Lyrics", "Lyrics", "720p", "1080p", "Video", "LYRICS"]


def get_user_input(prompt: str, default: Any) -> str:
    """Handles user input for functions that require interactivity

    Args:
        prompt (str): The message who'll be shown to the user
        default (Any): The default value to be suggested to the user

    Returns:
        str: The chosen user input
    """
    if prompt.endswith(":"):
        prompt = prompt[:-1]
    prompt = prompt.strip()
    if default:
        if str(default).lower() == "y":
            prompt = f"{prompt} [Y/n]"
        elif str(default).lower() == "n":
            prompt = f"{prompt} [y/N]"
        else:
            prompt = f"{prompt} [{default}]"
    user_input = input(prompt + ": ")

    if not user_input and default:
        return default

    return user_input


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
        suggested_title = channel + " - " + suggested_title

    for s in STRINGS_TO_REMOVE:
        suggested_title = suggested_title.replace(s, "")
    suggested_title = suggested_title.strip()

    should_update_title = "Y"
    if interactive and suggested_title != title:
        print("\n------------------------------")
        print("About to update title of song.")
        print(f"Original  title: {title}")
        print("Suggested title: " + Fore.BLUE + Back.WHITE + suggested_title + Fore.RESET + Back.RESET)

        should_update_title = get_user_input("Should use suggestion?", "Y")

    # Don't use suggestion, type manually
    if should_update_title.lower() != "y":
        suggested_title = get_user_input("Enter the name of the title manually", title)

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


# TODO - Isn't used anywhere atm.
def convert_to_filename(title: str) -> str:
    """Converts title to a file name.
       Used to handle edge cases where the title contains illegal file characters.

    Args:
        title (str): The title.

    Returns:
        str: The file name.
    """
    band, song = title.split(" - ")
    if band.startswith("DECO"):
        return "DECO*27" + " - " + song
    return title


# TODO - Isn't used anywhere atm.
def convert_from_filename(filename: str) -> str:
    """Converts filename to a title.
       Used to handle edge cases where the title contains illegal file characters.

    Args:
        title (str): The file name.

    Returns:
        str: The title.
    """
    band, song = filename.split(" - ")
    if band.startswith("DECO"):
        return "DECO_27" + " - " + song
    return filename


# TODO - consider changing this with `pick`
def print_suggestions(recordings: List[ReleaseRecording], artist: str, title: str, suggested_recording: int):
    """Prints the suggestions recordings.

    Args:
        recordings List[str, int, int]: The suggested recordings to print
        artist (str): The artist of the track
        title (str): The title of the track
        suggested_recording (int): The default recording to choose.
    """
    print("--------------------")
    print(f"Choose the correct album for {artist} - {title}:")
    print(" -1: Skip album metadata")
    print("--------------------")
    print(" 0 : Type metadata manually")
    print("--------------------")
    for index, recording in enumerate(recordings):
        if suggested_recording == index:  # Highlight suggested album
            print(Fore.BLUE, Back.WHITE, end="")
        print(f"{index + 1} : {recording.album}")
        print(f" >> year : {recording.year}, track : {recording.track}" + Fore.RESET + Back.RESET)
        print("--------------------")


def choose_recording(recordings: List[ReleaseRecording], suggested_recording: int) -> Optional[ReleaseRecording]:
    """Chooses a recording interactivly using user input.

    Args:
        recordings (List[ReleaseRecording]): List of suggested recordings.
        suggested_recording (int): Default index for recording from the recordings list.

    Returns:
        ReleaseRecording: Chosen Recording
    """
    recording_index = get_user_input("Enter the correct album number", default=suggested_recording + 1)
    recording_index = int(recording_index)
    # TODO - validate recording_index
    if not recordings:
        return None
    if recording_index == -1:
        return None  # No album information needed
    if recording_index == 0:
        # TODO - validate input
        album = get_user_input("Enter album name", default=recordings[suggested_recording].album)
        year = int(get_user_input("Enter album year", default=recordings[suggested_recording].year))
        track = int(get_user_input("Enter album track", default=recordings[suggested_recording].track))
        return ReleaseRecording(album, year, "", track, "")
    return recordings[recording_index - 1]


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


def get_suggested_recording(recordings: List[ReleaseRecording]) -> int:
    """Returns the index of a likely correct recording out of the recordings list using heurestics.

    Args:
        recordings (List[ReleaseRecording]): A sorted list (by year) of recordings to get suggestion from.

    Returns:
        int: Index of suggested recording, or -1 if there's no suggestion
    """
    # TODO - Instead of linear scan, run 'min' with a function, give score according to heuristics
    # e.g., year > 0 is worth 1000 points
    #       title contains forbidden works (hits, best), negative 200 points
    #       single, negative 10 points
    suggested_recording_index = -1
    potential_single_index = -1
    for recording_index, recording in enumerate(recordings):
        # Year is greater then 0
        if recording.year == 0:
            logger.debug("Skipping %s because year == 0", recording.album)
            continue
        if "hits" in recording.album.lower():
            logger.debug("Skipping %s because it contains hits", recording.album)
            continue
        if "live" in recording.album.lower():
            logger.debug("Skipping %s because it contains live", recording.album)
            continue
        if "best" in recording.album.lower():
            logger.debug("Skipping %s because it contains best", recording.album)
            continue

        date_from_album = extract_date_from_string(recording.album.lower())
        if date_from_album:
            logger.debug("Skipping %s because it contains date: %s", recording.album, str(date_from_album))
            continue
        if "promotion" in recording.status:
            logger.debug("Skipping %s because the status is promotional", recording.album)
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


class MP3MetaData:
    """Class that represents mp3 metadata."""

    def __init__(
        self,
        band: str,
        song: str,
        album: str = "",
        year: str = "",
        track: str = "",
        genre: str = "",
        art_path: str = "",
        art_configured: bool = False,
    ):
        self.band = band
        self.song = song
        self.album = album
        self.year = year
        self.track = track
        self.genre = genre
        self.art_path = art_path
        self.art_configured = art_configured

    @classmethod
    def from_file(cls, file_path: str, interactive: bool = False):
        """Initalized an instance of the class from a file and its metadata.

        Args:
            file_path (str): The path of the file.
            interactive (bool, optional): Whether can use user input to decide on names. Defaults to False.

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
        if not mp3_file:
            song, band, album, year, track, album_art, art_configured = "", "", "", "", "", "", False
        else:
            song = mp3_file.get("title").value
            band = mp3_file.get("artist").value
            album = mp3_file.get("album").value
            year = mp3_file.get("year").value
            track = mp3_file.get("tracknumber").value
            album_art = mp3_file.get("artwork")
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
            # TODO - use function get_artwork_path
            name_for_art = album if album else song
            album_artwork_path = join(IMG_DIR, f"{band} - {name_for_art}.png")

            # Extract image if it's not in the IMG DIR
            if not isfile(album_artwork_path):
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
            _type_: _description_
        """
        parent_directory_path = dirname(file_path)
        parent_directory = basename(parent_directory_path)
        # No album info if directory's pattern is not `ALBUM (YEAR)``
        path_match = re.match(r"(?P<album>.+) \((?P<year>\d{4})\)", parent_directory)
        if not path_match:
            return None

        grandparent_directory = basename(dirname(parent_directory))
        return (grandparent_directory, path_match.group("album"), int(path_match.group("year")))

    @property
    def title(self) -> str:
        """Get title (band - song)"""
        return self.band + " - " + self.song

    @title.setter
    def title(self, value: str):
        """Updates title"""
        # TODO - think what to do in more complex cases. Can I assume the artist doesn't have '-'?
        assert value.count(" - ") == 1
        self.band, self.song = value.split(" - ")

    def update_missing_fields(self, interactive: bool = False, keep_current_metadata: bool = False):
        """Updates missing mp3 metadata fields.
        Args:
            interactive (bool, optional): Should run in interactive mode, get user feedback regarding title fixes.
                                          Defaults to False.
            keep_current_metadata (bool, optional): States whether to use existing metadata.
                                                    USED ONLY IF interactive=False!
                                                    Defaults to False.
        """
        if not self.title:
            return

        # Check if there're missing fields
        if self.album and self.year and self.track:
            # Not interactive and keeping metadata, nothing to do
            if not interactive and keep_current_metadata:
                logger.debug("Keeping current metadata for %s", self.title)
                return
            if not interactive:
                should_use_existing_metadata = keep_current_metadata
            else:  # Interactive mode
                should_use_existing_metadata = get_user_input(
                    prompt=f"""Metadata already set.
{self.title}
album = {self.album}
year = {self.year}
track = {self.track}
Skip?""",
                    default="Y",
                )

            # TODO - handle user input
            if should_use_existing_metadata.lower() == "y":
                return

        # Get recording candidates
        artist, title = self.band, self.song
        recordings = get_track_info(artist, title)

        # Sort by release year (main), and by length of album (secondary)
        recordings.sort(key=lambda recording: (recording.year, len(recording.album)))

        suggested_album = get_suggested_recording(recordings)

        if not interactive:
            if not recordings:
                self.album = None
                self.year = 0
                self.album = None
                return
            suggested_album = max(suggested_album, 0)
            self.album = recordings[suggested_album].album
            self.year = recordings[suggested_album].year
            self.track = recordings[suggested_album].track
            return

        print_suggestions(recordings, artist, title, suggested_album)
        chosen_recording = choose_recording(recordings, suggested_album)

        self.album = chosen_recording.album
        self.year = chosen_recording.year
        self.track = chosen_recording.track

        logger.debug("Album: %s, year: %d, track: %d", self.album, self.year, self.track)

    def update_album_art(self):
        """Updates album artwork path. Downloads the artwork if necessary"""
        if not self.band:
            return

        if not (self.album or self.song):
            return

        name_for_art = self.album if self.album else self.song
        album_artwork_path = join(IMG_DIR, f"{self.band} - {name_for_art}.png")

        if not isfile(album_artwork_path):
            download_album_artwork(self.band, name_for_art, filepath=album_artwork_path)

        # Making sure the file does exist (in case download has failed)
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
    base_path: str, interactive: bool = True, update_album_art: bool = False, recursive: bool = False
):
    """Updates mp3 metadata of files in a directory.

    Args:
        base_path (str): Path of the directory that contains the mp3 files
        interactive (bool, optional): Should run in interactive mode. Defaults to True.
        update_album_art (bool, optional): Should update the album art of the files. Defaults to False.
        recursive (bool, optional): Should apply to subdirectories. Defaults to False.
    """
    if not os.path.isdir(base_path):
        logger.error("Provided base path %s is not an existing directory", base_path)
        sys.exit(1)

    paths = Path(base_path).rglob("*.mp3") if recursive else Path(base_path).glob("*.mp3")

    for path in paths:
        input(f"About to set data for {path.name}. Press enter to continue...")
        metadata = MP3MetaData.from_file(file_path=str(path.absolute()))
        metadata.update_missing_fields(interactive=interactive)

        if update_album_art:
            metadata.update_album_art()
        metadata.apply_on_file(file_path=path.absolute())
