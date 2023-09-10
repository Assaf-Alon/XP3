import unittest
from mp3_metadata import Song


class TestFixTitle(unittest.TestCase):
    def test_fix_title_no_changes(self):
        # Test if fix_title does not change the title if it's in the correct format
        v1 = Song("Band - Title", "Evil Channel >=D")
        self.assertEqual(v1.title, "Band - Title")

        v2 = Song("A New Better Band - Title, The Better Version", "Evil Channel >=D")
        self.assertEqual(v2.title, "A New Better Band - Title, The Better Version")

    def test_fix_title_illegal_chars(self):
        # Test if fix_title removes illegal characters from the title
        v1 = Song("Linkin Park - Paper#cut", "Linkin Park Fans ^^")
        self.assertEqual(v1.title, "Linkin Park - Papercut")

        v2 = Song("Linkin Park - Pap<e#r##c>ut", "Linkin Park")
        self.assertEqual(v2.title, "Linkin Park - Papercut")

        v3 = Song(
            'The Book Of Mormon: "I Believe"',
            "jbsdg",
        )
        self.assertEqual(v3.title, "The Book Of Mormon - I Believe")

    def test_fix_title_parentheses(self):
        # Test if fix_title removes content within parentheses
        v1 = Song(
            " System Of A Down - Toxicity (Official HD Video)",
            "System Of A Down",
        )
        self.assertEqual(v1.title, "System Of A Down - Toxicity")

        v2 = Song(
            '  Skillet - "Feel Invincible" [Official Music Video] ',
            "Skillet",
        )
        self.assertEqual(v2.title, "Skillet - Feel Invincible")

        v3 = Song(
            "Journey - Don't Stop Believin' (Official Audio)",
            "journey",
        )
        self.assertEqual(v3.title, "Journey - Don't Stop Believin'")

    def test_fix_title_hyphen(self):
        # Test if fix_title handles titles with hyphens
        v = Song(
            "Six Feet Under",
            "Smash Into Pieces",
        )
        self.assertEqual(v.title, "Smash Into Pieces - Six Feet Under")

    def test_fix_title_strings_to_remove(self):
        # Test if fix_title removes specified strings
        v1 = Song(
            "My Chemical Romance - Dead! Lyrics",
            "Muzic303",
        )
        self.assertEqual(v1.title, "My Chemical Romance - Dead!")

        v2 = Song(
            "My Chemical Romance - Dead! Lyrics 1080p (mega official video by Muzic303)",
            "Muzic303",
        )
        self.assertEqual(v2.title, "My Chemical Romance - Dead!")


if __name__ == "__main__":
    unittest.main()
