import pytube
import youtube_dl
import mutagen
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from moviepy.editor import *
import music_tag

from Song import Song
from music_api import get_track_info
from constants import MP3_DIR, MP4_DIR, DEFAULT_PLAYLIST

from os import listdir
from os.path import isfile, join, basename



def get_playlist_songs(playlist_url = DEFAULT_PLAYLIST, start_index = 0, end_index = 999999, interactive=True):    
    playlist = pytube.Playlist(playlist_url)
    print(f"Number of videos in playlist: {len(playlist.video_urls)}")
    start_index -= 1
    end_index = min(end_index - 1, len(playlist.video_urls))
    
    songs = []
    
    for index in range(start_index, end_index + 1):
        py_video = playlist.videos[index]
        song = Song(py_video.watch_url, py_video.title, py_video.author)
        song.fix_title(warn=interactive)
        song.update_album(interactive=interactive)
        songs.append(song)

    return songs

# Old
def update_album_metadata(base_dir):
    year = "N/A"
    
    only_dir = base_dir.split('\\')[-1]
    
    if '(' in only_dir:
        [album, year] = only_dir.split('(')
        album = album.rstrip()
        year = year[:-1]
    else:
        album = only_dir
    
    mp3_files = [f for f in listdir(base_dir) if isfile(join(base_dir, f))]
    for mp3 in mp3_files:
        m_str = base_dir + '\\' + mp3
        m = EasyID3(m_str)

        m['album'] = album
        # if year != "N/A": # Does not support year :(
        #     m['year'] = year
        m.save()


def update_metadata_from_path(filepath, interactive=True, update_album_artwork=False):
    filename = basename(filepath)
    print(filename)
    assert filename.endswith(".mp3")
    song_title = filename[:-4]
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
    mp3_path = base_dir + "\\" + song.title + ".mp3"
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

# Old
def update_artist_and_title_metadata(base_dir):
    
    mp3_files = [f for f in listdir(base_dir) if isfile(join(base_dir, f))]

    for mp3 in mp3_files:
        m_str = base_dir + '\\' + mp3
        try:
            meta = EasyID3(m_str)
        except mutagen.id3.ID3NoHeaderError:
            meta = mutagen.File(m_str, easy=True)
        #    if meta.tags:
            meta.delete()
            meta.add_tags()
        
        # meta = MP3(m_str)
        # meta.tags.delete()
        # meta.add_tags()
        
        [artist, title] = m_str.split('-')
        # [tmp, artist, title] = m_str.split('-')
        print(artist)
        artist = artist.split('\\')[-1]
        artist = artist[0:len(artist)-1]
        title = title[1:len(title)-4]

        if artist.lower().startswith("deco"):
            artist = "DECO*27"
        if artist.lower().startswith("p_"):
            artist = "P*Light"

        meta['artist'] = artist
        meta['ALBUMARTIST'] = artist
        meta['title'] = title
        meta.save(m_str, v1=2)
        print(f"Updated {artist} - {title}")

# Old
def download_ytvid_as_mp3(video_url, video_title=None):
    video_info = youtube_dl.YoutubeDL().extract_info(url = video_url,download=False)
    if not video_title:
        filename = video_info['title'] + ".mp3"
    else:
        filename = video_title
    filepath = MP3_DIR + "\\" + filename
    options={
        'format':'bestaudio/best',
        'keepvideo':False,
        'outtmpl':filepath,
    }

    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([video_info['webpage_url']])

    print(f" >> Finished downloading {filename}")


def download_ytvid(video_url, out_path=MP4_DIR, title=None):
    if title and not title.endswith(".mp4"):
        title = title + ".mp4"
    return pytube.YouTube(video_url).streams.filter(file_extension="mp4").first().download(output_path=out_path, filename=title)
        

def convert_mp4_to_mp3(mp4_path):
    assert mp4_path.endswith(".mp4")
    mp4_filename = basename(mp4_path)
    mp3_path = MP3_DIR + "\\" + mp4_filename[:-1] + "3"
    video = VideoFileClip(mp4_path)
    video.audio.write_audiofile(mp3_path)


def download_XPrimental(playlist_url = DEFAULT_PLAYLIST, start_index=0, end_index=99999, interactive=True, verbose=True):
    songs = get_playlist_songs(playlist_url=playlist_url start_index=start_index, end_index=end_index)
    for song in songs:
        if verbose:
            print(f" > Downloading {song.title}, from {song.url}")
        filename = download_ytvid(song.url, out_path=MP4_DIR, title=song.title)
        if verbose:
            print(f" >> Downloaded {filename}")
        convert_mp4_to_mp3(mp4_path=filename)
        update_metadata_from_song(MP3_DIR, song)
        if verbose:
            print(f" >> Updated metadata for {filename}")




# if __name__ == "__main__":
#     x = Song("", "Poets of the winter-Temple of thoughts (lyrics) 1080p", "")
#     x.fix_title()
#     print(x)
#     # videos = get_playlist_videos(start_index=9, end_index=9)
#     # for video in videos:
#     #     filename = download_ytvid(video.url, out_path=MP4_DIR, title=video.title)
#     #     print(f" >> Downloaded {filename}")
#     #     convert_mp4_to_mp3(mp4_path=filename)
    
#     # update_artist_and_title_metadata(MP3_DIR)