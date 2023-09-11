import unittest
from mp3_metadata import Song


class TestFixTitle(unittest.TestCase):
    def test_fix_title_no_changes(self):
        s1 = Song("Band - Title", "Evil Channel >=D")
        self.assertEqual(s1.title, "Band - Title")

        s2 = Song("A New Better Band - Title, The Better Version", "Evil Channel >=D")
        self.assertEqual(s2.title, "A New Better Band - Title, The Better Version")

    def test_fix_title_illegal_chars(self):
        s1 = Song("Linkin Park - Paper#cut", "Linkin Park Fans ^^")
        self.assertEqual(s1.title, "Linkin Park - Papercut")

        s2 = Song("Linkin Park - Pap<e#r##c>ut", "Linkin Park")
        self.assertEqual(s2.title, "Linkin Park - Papercut")

        v3 = Song(
            'The Book Of Mormon: "I Believe"',
            "jbsdg",
        )
        self.assertEqual(v3.title, "The Book Of Mormon - I Believe")

    def test_fix_title_parentheses(self):
        s1 = Song(
            " System Of A Down - Toxicity (Official HD Video)",
            "System Of A Down",
        )
        self.assertEqual(s1.title, "System Of A Down - Toxicity")

        s2 = Song(
            '  Skillet - "Feel Invincible" [Official Music Video] ',
            "Skillet",
        )
        self.assertEqual(s2.title, "Skillet - Feel Invincible")

        v3 = Song(
            "Journey - Don't Stop Believin' (Official Audio)",
            "journey",
        )
        self.assertEqual(v3.title, "Journey - Don't Stop Believin'")

    def test_fix_title_hyphen(self):
        v = Song(
            "Six Feet Under",
            "Smash Into Pieces",
        )
        self.assertEqual(v.title, "Smash Into Pieces - Six Feet Under")

    def test_fix_title_strings_to_remove(self):
        s1 = Song(
            "My Chemical Romance - Dead! Lyrics",
            "Muzic303",
        )
        self.assertEqual(s1.title, "My Chemical Romance - Dead!")

        s2 = Song(
            "My Chemical Romance - Dead! Lyrics 1080p (mega official video by Muzic303)",
            "Muzic303",
        )
        self.assertEqual(s2.title, "My Chemical Romance - Dead!")


if __name__ == "__main__":
    unittest.main()
