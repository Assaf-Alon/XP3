import unittest
from mp3_metadata import MP3MetaData
import os
from os.path import join, dirname
import shutil
from utils import get_file_md5_hash
from config import TMP_DIR


class TestUpdateAlbum(unittest.TestCase):
    bb_path = join(TMP_DIR, "Breaking Benjamin")
    song_path = join(join(bb_path, "Phobia (2006)"), "Breaking Benjamin - The Diary of Jane.mp3")

    def setUp(self):
        os.makedirs(dirname(self.song_path))
        open(self.song_path, "x").close()
        return super().setUp()

    def tearDown(self) -> None:
        shutil.rmtree(self.bb_path, ignore_errors=True)
        return super().tearDown()

    def test_update_album1(self):
        m1 = MP3MetaData.from_title(title="Skillet - Dominion")
        m1.update_missing_fields(interactive=False)
        self.assertEqual(m1.album, "Dominion")
        self.assertEqual(m1.year, 2022)
        self.assertEqual(m1.track, 3)

        m2 = MP3MetaData.from_video(channel="Smash Into Pieces", title="Wake Up")
        m2.update_missing_fields(interactive=False)
        self.assertEqual(m2.album, "Arcadia")
        self.assertEqual(m2.year, 2020)
        self.assertEqual(m2.track, 2)

    def test_update_album2(self):
        m1 = MP3MetaData.from_title("Smash Into Pieces-All Eyes on You")
        m1.update_missing_fields(interactive=False)
        self.assertEqual(m1.album, "Arcadia")
        self.assertEqual(m1.year, 2020)
        self.assertEqual(m1.track, 5)

        m2 = MP3MetaData.from_title(title="Smash Into Pieces -All eyes ON You")
        m2.update_missing_fields(interactive=False)
        self.assertEqual(m2.album, "Arcadia")
        self.assertEqual(m2.year, 2020)
        self.assertEqual(m2.track, 5)

    def test_update_image1(self):
        m1 = MP3MetaData.from_video(title="Rise Against - Audience of One")
        m1.update_missing_fields(interactive=False)
        self.assertEqual(m1.album, "Appeal to Reason")
        self.assertEqual(m1.year, 2008)
        self.assertEqual(m1.track, 8)

        m1.update_album_art()
        self.assertTrue(os.path.isfile(m1.art_path))
        self.assertEqual(get_file_md5_hash(m1.art_path), "52a26502a8073d857e1d147b52efc455")

        os.remove(m1.art_path)

    def test_from_file1(self):
        m1 = MP3MetaData.from_file(file_path=self.song_path)
        self.assertEqual(m1.band, "Breaking Benjamin")
        self.assertEqual(m1.song, "The Diary of Jane")
        self.assertEqual(m1.album, "Phobia")
        self.assertEqual(m1.year, 2006)


if __name__ == "__main__":
    unittest.main()
