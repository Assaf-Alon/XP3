"""Tests functions related to songs downloading """

import unittest

from mp3_download import get_playlist_songs


class TestDownloadSong(unittest.TestCase):
    """Tests songs downloading and playlist retrieval"""

    def test_get_playlist_songs1(self):
        """Tests the get_playlist_songs function"""
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
        """Tests the get_playlist_songs function"""
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
        """Tests the get_playlist_songs function"""
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

    # TODO - Test actual download song function
