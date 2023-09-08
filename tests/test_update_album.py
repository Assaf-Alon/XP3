import unittest
from mp3_metadata import Song


class TestUpdateAlbum(unittest.TestCase):
    def test_update_album1(self):
        v1 = Song(title="Skillet - Dominion")
        v1.fix_title(interactive=False)
        v1.update_album(interactive=False)
        self.assertEqual(v1.album, "Dominion")
        self.assertEqual(v1.year, 2022)
        self.assertEqual(v1.track, 3)

        v2 = Song(band="Smash Into Pieces", song="Wake Up")
        v2.fix_title(interactive=False)
        v2.update_album(interactive=False)
        self.assertEqual(v2.album, "Arcadia")
        self.assertEqual(v2.year, 2020)
        self.assertEqual(v2.track, 2)

    def test_update_album2(self):
        v1 = Song(band="Smash Into Pieces", song="All Eyes on You")
        v1.fix_title(interactive=False)
        v1.update_album(interactive=False)
        self.assertEqual(v1.album, "Arcadia")
        self.assertEqual(v1.year, 2020)
        self.assertEqual(v1.track, 5)

        v2 = Song(band="Smash Into Pieces", song="All eyes ON You")
        v2.fix_title(interactive=False)
        v2.update_album(interactive=False)
        self.assertEqual(v2.album, "Arcadia")
        self.assertEqual(v2.year, 2020)
        self.assertEqual(v2.track, 5)


if __name__ == "__main__":
    unittest.main()
