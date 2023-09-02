import re
from music_api import get_track_info, download_album_artwork
from constants import IMG_DIR
from colorama import Fore, Back, Style
from os import listdir
from os.path import isfile, join, basename
import music_tag

def get_user_input(prompt: str, default=None):
    if prompt.endswith(":"):
        prompt = prompt[:-1]
    prompt = prompt.strip()
    if default:
        prompt = f"{prompt} [{default}]"
    user_input = input(prompt + ": ")
    
    if not user_input:
        return default
    
    return user_input

class Song():
    pattern_illegal_chars = "[\^#$\"<>\|\+]"
    strings_to_remove = ["with Lyrics", "Lyrics", "720p", "1080p", "Video", "LYRICS"]
    
    def __init__(self, url="", title="", channel="", band="", song=""):
        # TODO - raise error instead
        assert title or (band and song)
        
        if band and song and not title:
            self.title = band + " - " + song
        
        # Not updating here in case the title is illegal
        # if self.title and (not self.band or not self.song):
        #     self.band, self.song = self.title.split(" - ")
        
        # TODO - consider adding "title_verified" or something like that
        self.url = url
        self.title = title
        self.channel = channel
        self.band = band
        self.song = song
        self.art_path = None
        
        
    def __repr__(self):
        if self.title:
            return self.title
        if self.song and self.band:
            return self.band + " - " + self.song
        return "Bad song"
    
    def __str__(self):
        if self.title:
            return self.title
        if self.song and self.band:
            return self.band + " - " + self.song
        return "Bad song"
    
    def fix_title(self, interactive=True):
        
        suggested_title = self.title
        
        # TODO - check if can swap band and song (via API calls?)
        
        # Swap colon (:) to hyphen (-)
        if suggested_title.find("-") < 0 and suggested_title.find(":") >= 0:
            suggested_title = suggested_title.replace(":", "-")
        
        # Remove illegal characters
        suggested_title = " ".join(re.sub(self.pattern_illegal_chars, "", suggested_title).split()).strip()
        
        # Remove parentheses (and content)
        pattern1 = r"\([^)]*\)"
        pattern2 = r"\[[^]]*\]"
        suggested_title = " ".join(re.sub(pattern1, "", suggested_title).split()).strip()
        suggested_title = " ".join(re.sub(pattern2, "", suggested_title).split()).strip()
        
        if suggested_title.find("-") >= 0:
            pattern3 = r"\s?-\s?"
            suggested_title = " ".join(re.sub(pattern3, " - ", suggested_title).split()).strip()
        elif self.channel:
            suggested_title = self.channel + " - " + suggested_title
        
        for s in self.strings_to_remove:
            suggested_title = suggested_title.replace(s, "")
        suggested_title = suggested_title.strip()
        
        should_update_title = ""
        if interactive and suggested_title != self.title:
            print("\n------------------------------")
            print("About to update title of song.")
            print(f"Original  title: {self.title}")
            print("Suggested title: " + Fore.BLUE + Back.WHITE + suggested_title + Fore.RESET + Back.RESET)
            should_update_title = input("Should use suggestion? [Y/n]")  # TODO - use get_user_input function
        
        if should_update_title == "" or should_update_title.lower() == "y":
            self.title = suggested_title
        else:
            self.title = input("Enter the name of the title manually: ")
        self.title = self.title.strip()
        self.band, self.song = self.title.split(" - ")
    
    def update_album(self, interactive=True):  # TODO - consider changing to update_album_info or something like that
        artist, title = self.band, self.song
        if not (self.band and self.song):
            artist, title = self.title.split(" - ")
        
        # Get album candidates
        albums = get_track_info(artist, title)
        
        # if len(albums) == 0:
        #     return
        
        # Sort by release year (main), and by length of album (secondary)
        albums.sort(key=lambda a: (a[1], len(a[0])))
        
        if not interactive:
            self.album = albums[0][0]
            self.year  = albums[0][1]
            self.track = albums[0][2]
            return
        
        suggested_album = -1
        for album_index in range(len(albums)):
            # Year is greater then 0
            if albums[album_index][1] > 0:
                suggested_album = album_index
                break
        
        print("--------------------")
        print(f"Choose the correct album for {artist} - {title}:")
        print(" -1: Skip album metadata")
        print("--------------------")
        print(" 0 : Type metadata manually")
        print("--------------------")
        for index, album in enumerate(albums):
            if (suggested_album == index): # Highlight suggested album
                print(Fore.BLUE, Back.WHITE, end='')
            print(f"{index + 1} : {album[0]}")
            print(f" >> year : {album[1]}, track : {album[2]}" + Fore.RESET + Back.RESET)
            print("--------------------")

        album_index = get_user_input("Enter the correct album number", default=suggested_album + 1)        
        album_index = int(album_index)
        if not albums:
            albums = [(None, None, None)]
        if album_index == -1:
            return  # No album information needed
        elif album_index == 0:
            self.album = get_user_input("Enter album name",  default=albums[suggested_album][0])
            self.year  = get_user_input("Enter album year",  default=albums[suggested_album][1])
            self.track = get_user_input("Enter album track", default=albums[suggested_album][2])
        else:
            self.album = albums[album_index - 1][0]
            self.year  = albums[album_index - 1][1]
            self.track = albums[album_index - 1][2]
            
        print(f"Album: {self.album}, year: {self.year}, track: {self.track}")
        # TODO - change all prints to logging
    
    def update_image(self):
        # TODO - raise error
        assert self.band and (self.album or self.song)  # TODO - standardize this
        name_for_art = self.album if self.album else self.song
        album_artwork_path = join(IMG_DIR, f"{self.band} - {name_for_art}.png")
        
        if not isfile(album_artwork_path):
            download_album_artwork(self.band, self.album, filepath=album_artwork_path)
        
        # Making sure the file does exist (in case download has failed)
        if isfile(album_artwork_path):
            self.art_path = album_artwork_path
            return
        
def convert_to_filename(title):
    band, song = title.split(" - ")
    if band.startswith("DECO"):
        return "DECO*27" + " - " + song
    return title

def convert_from_filename(title):
    band, song = title.split(" - ")
    if band.startswith("DECO"):
        return "DECO_27" + " - " + song
    return title

# TODO - use this to load metadata if exists, and process song name (DECO)
def load_song_from_file(filepath):
    pass

def update_metadata_from_path(filepath, interactive=True, update_album_artwork=False):
    filename = basename(filepath)
    print(filename)
    assert filename.endswith(".mp3")
    song_title = convert_to_filename(title=filename[:-4])
    
    # TODO - read metadata if exists
    song = Song(title=song_title)
    song.fix_title()
    song.update_album(interactive=interactive)
    song.update_image()
    
    file = music_tag.load_file(filepath) # type: music_tag.id3.Mp3File
    print(song)
    file['title']  = song.song
    file['artist'] = song.band
    file['albumartist'] = song.band
    if song.year:
        file['year'] = song.year
    if song.album:
        file['album'] = song.album
    if song.track:
        file['tracknumber'] = song.track
    if update_album_artwork and song.art_path:
        with open(song.art_path, 'rb') as img:
            file['artwork'] = img.read()
    file.save()
 
def update_metadata_from_directory(basepath, interactive=True, update_album_artwork=False):
    try:
        mp3_files = [basepath + f for f in listdir(basepath) if isfile(join(basepath, f))]
    except FileNotFoundError:
        print(f"Base path {basepath} doesn't exist")
        exit(1)
    for file in mp3_files:
        if file.endswith(".mp3"):
            update_metadata_from_path(filepath=file, interactive=interactive, update_album_artwork=update_album_artwork)
 
def update_metadata_from_song(base_dir, song: Song):
    mp3_path = join(base_dir, song.title + ".mp3")
    # mp3_path = base_dir + "\\" + song.title + ".mp3"
    file = music_tag.load_file(mp3_path) # type: music_tag.id3.Mp3File
    
    artist = song.band
    if artist.lower().startswith("deco"):
        artist = "DECO*27"
    if artist.lower().startswith("p_"):
        artist = "P*Light"
    
    file['title']       = song.song
    file['artist']      = artist
    file['year']        = song.year
    file['album']       = song.album
    file['albumartist'] = artist
    file['tracknumber'] = song.track
    
    if song.art_path:
        with open(song.art_path, 'rb') as img:
            file['artwork'] = img.read()
    
    file.save()

    print(f"Updated {song.band} - {song.song}")