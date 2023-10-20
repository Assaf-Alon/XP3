"""Tests functions related to songs downloading """
import hashlib
import os
import unittest

from config import TMP_DIR
from mp3 import download_ytvid, get_playlist_songs


class TestDownloadSong(unittest.TestCase):
    def test_get_playlist_songs1(self):
        playlist_url = "https://www.youtube.com/playlist?list=PLGN96WAC2Fv2DNdIbAHQsGVO3IxNawtu4"

        songs = get_playlist_songs(
            playlist_url=playlist_url,
            start_index=1,
            end_index=1,
            interactive=False,
        )
        self.assertEqual(len(songs), 1)
        song, url = songs[0]

        self.assertEqual(url, "https://youtube.com/watch?v=2f_0HSWLDLg")
        self.assertEqual(song.song, "The Stage")
        self.assertEqual(song.band, "Avenged Sevenfold")
        self.assertEqual(song.title, "Avenged Sevenfold - The Stage")
        self.assertEqual(song.album, "The Stage")
        self.assertEqual(song.year, 2016)
        self.assertEqual(song.track, 1)

    def test_get_playlist_songs2(self):
        playlist_url = "https://www.youtube.com/playlist?list=PLGN96WAC2Fv2DNdIbAHQsGVO3IxNawtu4"
        songs = get_playlist_songs(
            playlist_url=playlist_url,
            start_index=2,
            end_index=2,
            interactive=False,
        )
        self.assertEqual(len(songs), 1)
        song, url = songs[0]

        self.assertEqual(url, "https://youtube.com/watch?v=OD819p2fM1c")
        self.assertEqual(song.song, "Paradigm")
        self.assertEqual(song.band, "Avenged Sevenfold")
        self.assertEqual(song.title, "Avenged Sevenfold - Paradigm")
        self.assertEqual(song.album, "The Stage")
        self.assertEqual(song.year, 2016)
        self.assertEqual(song.track, 2)

    def test_get_playlist_songs3(self):
        playlist_url = "https://www.youtube.com/playlist?list=PLGN96WAC2Fv2DNdIbAHQsGVO3IxNawtu4"
        songs = get_playlist_songs(
            playlist_url=playlist_url,
            start_index=4,
            end_index=5,
            interactive=False,
        )
        self.assertEqual(len(songs), 2)

        song = songs[0][0]
        self.assertEqual(song.song, "God Damn")
        self.assertEqual(song.band, "Avenged Sevenfold")
        self.assertEqual(song.title, "Avenged Sevenfold - God Damn")
        self.assertEqual(song.album, "The Stage")
        self.assertEqual(song.year, 2016)
        self.assertEqual(song.track, 4)

        song = songs[1][0]
        self.assertEqual(song.song, "Creating God")
        self.assertEqual(song.band, "Avenged Sevenfold")
        self.assertEqual(song.title, "Avenged Sevenfold - Creating God")
        self.assertEqual(song.album, "The Stage")
        self.assertEqual(song.year, 2016)
        self.assertEqual(song.track, 5)

    @unittest.skip("Heavy test")
    def test_download_ytvid1(self):
        playlist_url = "https://www.youtube.com/playlist?list=PLGN96WAC2Fv2DNdIbAHQsGVO3IxNawtu4"

        songs = get_playlist_songs(
            playlist_url=playlist_url,
            start_index=1,
            end_index=1,
            interactive=False,
        )

        song, url = songs[0]

        download_ytvid(url, out_path=TMP_DIR, title=song.title)
        song_path = os.path.join(TMP_DIR, song.title) + ".mp4"

        with open(song_path, "rb") as song_file:
            data = song_file.read()
            song_md5 = hashlib.md5(data).hexdigest()
        self.assertEqual(song_md5, "b788d8de3365ea1789b42e5fcd4a7782")

        os.remove(song_path)
