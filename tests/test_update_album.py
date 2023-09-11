import unittest
from mp3_metadata import Song
from constants import MP4_DIR
import os
from utils import get_file_md5_hash


class TestUpdateAlbum(unittest.TestCase):
    def test_update_album1(self):
        s1 = Song(title="Skillet - Dominion")
        s1.update_album_info(interactive=False)
        self.assertEqual(s1.album, "Dominion")
        self.assertEqual(s1.year, 2022)
        self.assertEqual(s1.track, 3)

        s2 = Song(band="Smash Into Pieces", song="Wake Up")
        s2.update_album_info(interactive=False)
        self.assertEqual(s2.album, "Arcadia")
        self.assertEqual(s2.year, 2020)
        self.assertEqual(s2.track, 2)

    def test_update_album2(self):
        s1 = Song(band="Smash Into Pieces", song="All Eyes on You")
        s1.update_album_info(interactive=False)
        self.assertEqual(s1.album, "Arcadia")
        self.assertEqual(s1.year, 2020)
        self.assertEqual(s1.track, 5)

        s2 = Song(band="Smash Into Pieces", song="All eyes ON You")
        s2.update_album_info(interactive=False)
        self.assertEqual(s2.album, "Arcadia")
        self.assertEqual(s2.year, 2020)
        self.assertEqual(s2.track, 5)

    def test_update_image1(self):
        s = Song(band="Rise Against", song="Audience of One")
        s.update_album_info(interactive=False)
        self.assertEqual(s.album, "Appeal to Reason")
        self.assertEqual(s.year, 2008)
        self.assertEqual(s.track, 8)

        s.update_image()
        self.assertTrue(os.path.exists(s.art_path))
        self.assertEqual(
            get_file_md5_hash(s.art_path), "d908c562d2d7645bef3869a7d250b9e4"
        )

        os.remove(s.art_path)


if __name__ == "__main__":
    unittest.main()
