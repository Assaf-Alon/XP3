"""Tests that the MP3MetaData class updates the missing fields correctly using an external API"""
import os
import shutil
import unittest
from os.path import dirname, join

from utils import get_file_md5_hash

from config import TMP_DIR
from mp3_metadata import MP3MetaData


class TestUpdateAlbum(unittest.TestCase):
    """Class for testing album information update on creation of MP3MetaData"""

    bb_path = join(TMP_DIR, "Breaking Benjamin")
    song_path = join(join(bb_path, "Phobia (2006)"), "Breaking Benjamin - The Diary of Jane.mp3")

    def setUp(self):
        """Creates files for testing purposes"""
        os.makedirs(dirname(self.song_path))
        open(self.song_path, "x", encoding="utf-8").close()  # pylint: disable=consider-using-with
        return super().setUp()

    def tearDown(self) -> None:
        """Removes files created for testing purposes"""
        shutil.rmtree(self.bb_path, ignore_errors=True)
        return super().tearDown()

    def test_update_album1(self):
        """Tests the update_missing_fields method"""
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
        """Tests the update_missing_fields method"""
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
        """Tests the update_album_art method"""
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
        """Tests MP3MetaData.from_file(...)"""
        m1 = MP3MetaData.from_file(file_path=self.song_path)
        self.assertEqual(m1.band, "Breaking Benjamin")
        self.assertEqual(m1.song, "The Diary of Jane")
        self.assertEqual(m1.album, "Phobia")
        self.assertEqual(m1.year, 2006)

    def test_update_album_singles(self):
        """
        Tests specific edge cases where singles were released, and later
        added to an album.
        """
        # Dragonforce - Cry Thunder
        m1 = MP3MetaData.from_title(title="Dragonforce - Cry Thunder")
        m1.update_missing_fields(interactive=False)
        self.assertEqual(m1.album, "The Power Within")
        self.assertEqual(m1.year, 2012)
        self.assertEqual(m1.track, 3)

        # Avenged Sevenfold - Bat Country
        m2 = MP3MetaData.from_title(title="Avenged Sevenfold - Bat Country")
        m2.update_missing_fields(interactive=False)
        self.assertEqual(m2.album, "City of Evil")
        self.assertEqual(m2.year, 2005)
        self.assertEqual(m2.track, 4)

        # Breaking Benjamin - Polyamorous
        m2 = MP3MetaData.from_title(title="Breaking Benjamin - Polyamorous")
        m2.update_missing_fields(interactive=False)
        self.assertEqual(m2.album, "Saturate")
        self.assertEqual(m2.year, 2002)
        self.assertEqual(m2.track, 3)

        # Bad Wolves - Zombie
        m2 = MP3MetaData.from_title(title="Bad Wolves - Zombie")
        m2.update_missing_fields(interactive=False)
        self.assertEqual(m2.album, "Disobey")
        self.assertEqual(m2.year, 2018)
        self.assertEqual(m2.track, 4)


if __name__ == "__main__":
    unittest.main()
