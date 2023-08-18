import re
from music_api import get_track_info, download_album_artwork
from constants import IMG_DIR
from colorama import Fore, Back, Style

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

    
    
    def __init__(self, url=None, title=None, channel=None, band=None, song=None):
        # TODO - raise error instead
        assert title or (band and song)
        
        self.url = url
        self.title = title
        self.channel = channel
        self.band = band
        self.song = song
        self.art_path = None
        
        if band and song and not title:
            self.title = band + " - " + song
        
        # Not updating here in case the title is illegal
        # if self.title and (not self.band or not self.song):
        #     self.band, self.song = self.title.split(" - ")
        
    def __str__(self):
        if self.title:
            return self.title
        if self.song and self.band:
            return self.band + " - " + self.song
        return "Bad song"
    
    def fix_title(self, warn=True):
        
        suggested_title = self.title
        
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
        if warn and suggested_title != self.title:
            print("\n------------------------------")
            print("About to update title of song.")
            print(f"Original  title: {self.title}")
            print("Suggested title: " + Fore.BLUE + Back.WHITE + suggested_title + Fore.RESET + Back.RESET)
            should_update_title = input("Should use suggestion? [Y/n]")
        
        if should_update_title == "" or should_update_title.lower() == "y":
            self.title = suggested_title
        else:
            self.title = input("Enter the name of the title manually: ")
        self.title = self.title.strip()
        self.band, self.song = self.title.split(" - ")
    
    def update_album(self, interactive=True):
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
    
    def update_image(self):
        # TODO - raise error
        assert self.band and self.album and self.title
        album_artwork_path = IMG_DIR + self.title + ".png"
        download_album_artwork(self.band, self.album, filepath=album_artwork_path)
        self.art_path = album_artwork_path