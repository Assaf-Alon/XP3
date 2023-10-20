import re
from typing import Any, List, Tuple

from music_api import get_track_info, download_album_artwork
from config import IMG_DIR, IS_DEBUG
from colorama import Fore, Back
from os import listdir
from os.path import isfile, join, basename, dirname
import music_tag
import logging

logger = logging.getLogger("XP3")
logger.setLevel(logging.DEBUG if IS_DEBUG else logging.INFO)

pattern_illegal_chars = r'[\\/:*?"<>|]'
strings_to_remove = ["with Lyrics", "Lyrics", "720p", "1080p", "Video", "LYRICS"]


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
    if suggested_title.find("-") < 0 and suggested_title.find(":") >= 0:
        suggested_title = suggested_title.replace(":", "-")

    # Remove illegal characters
    suggested_title = " ".join(re.sub(pattern_illegal_chars, "", suggested_title).split()).strip()

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

    for s in strings_to_remove:
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
    band, song = title.split(" - ")
    if band.startswith("DECO"):
        return "DECO*27" + " - " + song
    return title


# TODO - Isn't used anywhere atm.
def convert_from_filename(title: str) -> str:
    band, song = title.split(" - ")
    if band.startswith("DECO"):
        return "DECO_27" + " - " + song
    return title


# TODO - consider changing this with `pick`
def print_suggestions(albums: List[Tuple[str, int, int]], artist: str, title: str, suggested_album: int):
    """Prints the suggestions for album-year-track trios.

    Args:
        albums List[str, int, int]: The suggested albums to print
        artist (str): The artist of the track
        title (str): The title of the track
        suggested_album (int): The default album to choose.
    """
    print("--------------------")
    print(f"Choose the correct album for {artist} - {title}:")
    print(" -1: Skip album metadata")
    print("--------------------")
    print(" 0 : Type metadata manually")
    print("--------------------")
    for index, album in enumerate(albums):
        if suggested_album == index:  # Highlight suggested album
            print(Fore.BLUE, Back.WHITE, end="")
        print(f"{index + 1} : {album[0]}")
        print(f" >> year : {album[1]}, track : {album[2]}" + Fore.RESET + Back.RESET)
        print("--------------------")


def choose_album(albums: List[Tuple[str, int, int]], suggested_album: int) -> Tuple[str, int, int]:
    """Chooses an album interactivly using user input.

    Args:
        albums (List[Tuple[str, int, int]]): List of suggested albums.
        suggested_album (int): Default index for album from the albums list.

    Returns:
        Tuple[str, int, int]: Tuple with chosen album, year, track
    """
    album_index = get_user_input("Enter the correct album number", default=suggested_album + 1)
    album_index = int(album_index)
    if not albums:
        albums = [("", 0, 0)]
    if album_index == -1:
        return ("", 0, 0)  # No album information needed
    elif album_index == 0:
        album = get_user_input("Enter album name", default=albums[suggested_album][0])
        year = get_user_input("Enter album year", default=albums[suggested_album][1])
        track = get_user_input("Enter album track", default=albums[suggested_album][2])
    else:
        album = albums[album_index - 1][0]
        year = albums[album_index - 1][1]
        track = albums[album_index - 1][2]
    year = int(year)
    track = int(track)
    return (album, year, track)


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


def get_suggested_album(albums: List[Tuple[str, int, int]]) -> int:
    """Returns the index of a likely correct album out of the albums list using heurestics.

    Args:
        albums (List[Tuple[str, int, int]]): List of albums to get suggestion from.

    Returns:
        int: Index of suggested album, or -1 if there's no suggestion
    """
    suggested_album = -1
    for album_index in range(len(albums)):
        # Year is greater then 0
        if albums[album_index][1] == 0:
            continue
        if "hits" in albums[album_index][0].lower():
            continue
        if "live" in albums[album_index][0].lower():
            continue
        if albums[album_index][1] > 0:
            suggested_album = album_index
            break
    return suggested_album


class MP3MetaData:
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
        except Exception:
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
                year = int(album_info[2])

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
    def extract_album_info_from_path(file_path: str):
        parent_directory_path = dirname(file_path)
        parent_directory = basename(parent_directory_path)
        # No album info if directory's pattern is not `ALBUM (YEAR)``
        path_match = re.match(r"(?P<album>.+) \((?P<year>\d{4})\)", parent_directory)
        if not path_match:
            return None

        grandparent_directory = basename(dirname(parent_directory))
        return (grandparent_directory, path_match.group("album"), path_match.group("year"))

    @property
    def title(self) -> str:
        return self.band + " - " + self.song

    @title.setter
    def title(self, value: str):
        # TODO - think what to do in more complex cases. Can I assume the artist doesn't have '-'?
        assert value.count(" - ") == 1
        self.band, self.song = value.split(" - ")

    def update_missing_fields(self, interactive: bool = False, keep_current_metadata: bool = False):
        # TODO - Docstring
        if not self.title:
            return

        # Check if there're missing fields
        if self.album and self.year and self.track:
            if not interactive:
                return
            should_use_existing_metadata = True
            if not keep_current_metadata:
                should_use_existing_metadata = get_user_input(
                    prompt=f"""Metadata already set.
{self.title}
album = {self.album}
year = {self.year}
track = {self.track}
Skip?""",
                    default="Y",
                )

            if should_use_existing_metadata.lower() == "y":
                return

        # Get album candidates
        artist, title = self.band, self.song
        albums = get_track_info(artist, title)

        # Sort by release year (main), and by length of album (secondary)
        albums.sort(key=lambda a: (a[1], len(a[0])))

        suggested_album = get_suggested_album(albums)

        if not interactive:
            if not albums:
                self.album = None
                self.year = 0
                self.album = None
                return
            suggested_album = max(suggested_album, 0)
            self.album = albums[suggested_album][0]
            self.year = albums[suggested_album][1]
            self.track = albums[suggested_album][2]
            return

        print_suggestions(albums, artist, title, suggested_album)
        self.album, self.year, self.track = choose_album(albums, suggested_album)

        logger.debug(f"Album: {self.album}, year: {self.year}, track: {self.track}")

    def update_album_art(self):
        # TODO - Docstring
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
        # TODO - Docstring
        if not isfile(file_path):
            logger.error(f"File not found: {file_path}")
            return

        mp3_file = music_tag.load_file(file_path)
        if not mp3_file:
            logger.error(f"Failed to load {file_path}")
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


def update_metadata_for_directory(base_path: str, interactive: bool = True, update_album_art: bool = False):
    # TODO - Docstring
    try:
        mp3_files = [join(base_path, f) for f in listdir(base_path) if isfile(join(base_path, f))]
    except FileNotFoundError:
        print(f"Base path {base_path} doesn't exist")
        exit(1)
    for file_path in mp3_files:
        if not file_path.endswith(".mp3"):
            continue
        metadata = MP3MetaData.from_file(file_path)
        metadata.update_missing_fields(interactive=interactive)
        if update_album_art:
            metadata.update_album_art()
        metadata.apply_on_file(file_path)
