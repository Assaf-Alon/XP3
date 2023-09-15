import re
from music_api import get_track_info, download_album_artwork
from constants import IMG_DIR, IS_DEBUG
from colorama import Fore, Back
from os import listdir
from os.path import isfile, join, basename, splitext
import music_tag
import logging

logger = logging.getLogger("XP3")
logger.setLevel(logging.DEBUG if IS_DEBUG else logging.INFO)

pattern_illegal_chars = '[\^#$"<>\|\+]'
strings_to_remove = ["with Lyrics", "Lyrics", "720p", "1080p", "Video", "LYRICS"]


def get_user_input(prompt: str, default: str = None):
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

    if not user_input:
        return default

    return user_input


# TODO - Handle DECO here
def get_title_suggestion(
    title: str = "", band: str = "", song: str = "", channel="", interactive=False
):
    assert (band and song) or title

    if band and song:
        title = band + " - " + song

    suggested_title = title

    # Swap colon (:) with hyphen (-)
    if suggested_title.find("-") < 0 and suggested_title.find(":") >= 0:
        suggested_title = suggested_title.replace(":", "-")

    # Remove illegal characters
    suggested_title = " ".join(
        re.sub(pattern_illegal_chars, "", suggested_title).split()
    ).strip()

    # Remove parentheses (and content)
    pattern1 = r"\([^)]*\)"
    pattern2 = r"\[[^]]*\]"
    suggested_title = " ".join(re.sub(pattern1, "", suggested_title).split()).strip()
    suggested_title = " ".join(re.sub(pattern2, "", suggested_title).split()).strip()

    # Dash whitespace
    if suggested_title.find("-") >= 0:
        pattern3 = r"\s?-\s?"
        suggested_title = " ".join(
            re.sub(pattern3, " - ", suggested_title).split()
        ).strip()

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
        print(
            "Suggested title: "
            + Fore.BLUE
            + Back.WHITE
            + suggested_title
            + Fore.RESET
            + Back.RESET
        )

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
        band, song = "ERROR", "ERROR"

    band = band.strip()
    song = song.strip()
    return band, song


def convert_to_filename(title: str) -> str:
    band, song = title.split(" - ")
    if band.startswith("DECO"):
        return "DECO*27" + " - " + song
    return title


def convert_from_filename(title: str) -> str:
    band, song = title.split(" - ")
    if band.startswith("DECO"):
        return "DECO_27" + " - " + song
    return title


def print_suggestions(albums, artist, title, suggested_album):
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


def choose_album(albums, suggested_album):
    album_index = get_user_input(
        "Enter the correct album number", default=suggested_album + 1
    )
    album_index = int(album_index)
    if not albums:
        albums = [(None, None, None)]
    if album_index == -1:
        return ("", "", "")  # No album information needed
    elif album_index == 0:
        album = get_user_input("Enter album name", default=albums[suggested_album][0])
        year = get_user_input("Enter album year", default=albums[suggested_album][1])
        track = get_user_input("Enter album track", default=albums[suggested_album][2])
    else:
        album = albums[album_index - 1][0]
        year = albums[album_index - 1][1]
        track = albums[album_index - 1][2]
    return (album, year, track)


def get_title_from_path(file_path: str):
    file_name = basename(file_path)
    assert file_name.endswith(".mp3")
    file_name_no_extension = file_name[:-4]
    return file_name_no_extension


class MP3MetaData:
    def __init__(
        self,
        band,
        song,
        album="",
        year="",
        track="",
        genre="",
        art_path="",
        art_configured=False,
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
        assert file_path.endswith(".mp3")

        mp3_file = music_tag.load_file(file_path)  # type: music_tag.id3.Mp3File
        song = mp3_file.get("title").value
        band = mp3_file.get("artist").value
        album = mp3_file.get("album").value
        year = mp3_file.get("year").value
        track = mp3_file.get("tracknumber").value
        album_art = mp3_file.get("artwork")
        art_configured = bool(album_art)
        album_artwork_path = ""

        if not (song and band):
            title = get_title_from_path(file_path)
            song, band = get_title_suggestion(title, interactive=interactive)

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
        band, song = get_title_suggestion(title=title, interactive=interactive)
        return cls(band=band, song=song)

    @classmethod
    def from_video(cls, title: str, channel: str = "", interactive: bool = False):
        band, song = get_title_suggestion(
            title=title, channel=channel, interactive=interactive
        )
        return cls(band=band, song=song)

    @property
    def title(self):
        return self.band + " - " + self.song

    @title.setter
    def title(self, value: str):
        assert value.count(" - ") == 1
        self.band, self.song = value.split(" - ")

    def update_missing_fields(self, interactive: bool = False):
        if not (self.band and self.song):
            return

        # Check if there're missing fields
        if self.album and self.year and self.track:
            if not interactive:
                return
            should_use_existing_metadata = get_user_input(
                prompt=f"Metadata already set.\n{self.title}\nalbum = {self.album}\nyear = {self.year}\ntrack = {self.track}\nSkip?",
                default="Y",
            )

            if should_use_existing_metadata:
                return

        # Get album candidates
        artist, title = self.band, self.song
        albums = get_track_info(artist, title)

        # if len(albums) == 0:
        #     return

        # Sort by release year (main), and by length of album (secondary)
        albums.sort(key=lambda a: (a[1], len(a[0])))

        suggested_album = -1
        for album_index in range(len(albums)):
            # Year is greater then 0
            if albums[album_index][1] > 0:
                suggested_album = album_index
                break

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
        assert self.band and (self.album or self.song)
        name_for_art = self.album if self.album else self.song
        album_artwork_path = join(IMG_DIR, f"{self.band} - {name_for_art}.png")

        if not isfile(album_artwork_path):
            download_album_artwork(self.band, self.album, filepath=album_artwork_path)

        # Making sure the file does exist (in case download has failed)
        if isfile(album_artwork_path):
            self.art_path = album_artwork_path

    def apply_on_file(self, file_path: str):
        if not isfile(file_path):
            logger.error(f"File not found: {file_path}")
            return

        file = music_tag.load_file(file_path)  # type: music_tag.id3.Mp3File
        if self.song:
            file["title"] = self.song

        if self.band:
            file["artist"] = self.band
            file["albumartist"] = self.band

        if self.year:
            file["year"] = self.year

        if self.album:
            file["album"] = self.album

        if self.track:
            file["tracknumber"] = self.track

        if self.art_path:
            with open(self.art_path, "rb") as img:
                file["artwork"] = img.read()

        file.save()

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
    base_path: str, interactive: bool = True, update_album_art: bool = False
):
    try:
        mp3_files = [
            join(base_path, f) for f in listdir(base_path) if isfile(join(base_path, f))
        ]
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


# def update_metadata_from_directory(
#     basepath: str, interactive: bool = True, update_album_artwork: bool = False
# ):
#     try:
#         mp3_files = [
#             basepath + f for f in listdir(basepath) if isfile(join(basepath, f))
#         ]
#     except FileNotFoundError:
#         print(f"Base path {basepath} doesn't exist")
#         exit(1)
#     for file in mp3_files:
#         if file.endswith(".mp3"):
#             update_metadata_from_path(
#                 filepath=file,
#                 interactive=interactive,
#                 update_album_artwork=update_album_artwork,
#             )


# def update_metadata_from_song(base_dir: str, song: Song):
#     mp3_path = join(base_dir, song.title + ".mp3")
#     # mp3_path = base_dir + "\\" + song.title + ".mp3"
#     file = music_tag.load_file(mp3_path)  # type: music_tag.id3.Mp3File

#     artist = song.band
#     if artist.lower().startswith("deco"):
#         artist = "DECO*27"
#     if artist.lower().startswith("p_"):
#         artist = "P*Light"

#     file["title"] = song.song
#     file["artist"] = artist
#     file["year"] = song.year
#     file["album"] = song.album
#     file["albumartist"] = artist
#     file["tracknumber"] = song.track

#     if song.art_path:
#         with open(song.art_path, "rb") as img:
#             file["artwork"] = img.read()

#     file.save()

#     logger.debug(f"Updated {song.band} - {song.song}")
