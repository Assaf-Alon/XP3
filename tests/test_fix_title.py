"""Tests that the method used to suggest a fixed title works as expected"""
import unittest

from mp3_metadata import MP3MetaData


class TestFixTitle(unittest.TestCase):
    """Tests that verify title fixing on creation"""

    def test_fix_title_no_changes(self):
        """Tests valid metadata creation"""
        m1 = MP3MetaData.from_video(title="Band - Title", channel="Evil Channel >=D")
        self.assertEqual(m1.title, "Band - Title")

        m2 = MP3MetaData.from_title(title="A New Better Band - Title, The Better Version")
        self.assertEqual(m2.title, "A New Better Band - Title, The Better Version")
        self.assertEqual(m2.band, "A New Better Band")
        self.assertEqual(m2.song, "Title, The Better Version")

    def test_fix_title_illegal_chars(self):
        """Tests removal of illegal characters"""
        m1 = MP3MetaData.from_video(title="Linkin Park - Paper?cut", channel="Linkin Park Fans ^^")
        self.assertEqual(m1.title, "Linkin Park - Papercut")

        m2 = MP3MetaData.from_video(title="Linkin Park - Pap<e?r\\/c>ut", channel="Linkin Park")
        self.assertEqual(m2.title, "Linkin Park - Papercut")

        m3 = MP3MetaData.from_video(
            title='The Book Of Mormon: "I Believe"',
            channel="jbsdg",
        )
        self.assertEqual(m3.title, "The Book Of Mormon - I Believe")

    def test_fix_title_parentheses(self):
        """Tests removal of parantheses (heuristic)"""
        m1 = MP3MetaData.from_video(
            title=" System Of A Down - Toxicity (Official HD Video)",
            channel="System Of A Down",
        )
        self.assertEqual(m1.title, "System Of A Down - Toxicity")

        m2 = MP3MetaData.from_video(
            title='  Skillet - "Feel Invincible" [Official Music Video] ',
            channel="Skillet",
        )
        self.assertEqual(m2.title, "Skillet - Feel Invincible")

        m3 = MP3MetaData.from_video(
            title="Journey - Don't Stop Believin' (Official Audio)",
            channel="journey",
        )
        self.assertEqual(m3.title, "Journey - Don't Stop Believin'")

    def test_fix_title_channel1(self):
        """Tests that title was created correctly with band implicitly stated in the channel"""
        m1 = MP3MetaData.from_video(
            title="Six Feet Under",
            channel="Smash Into Pieces",
        )
        self.assertEqual(m1.title, "Smash Into Pieces - Six Feet Under")

        m2 = MP3MetaData.from_video("Smash Into Pieces - Six Feet Under")
        self.assertEqual(m2.title, "Smash Into Pieces - Six Feet Under")

    def test_fix_title_channel2(self):
        """Tests that title was created correctly with band implicitly stated in the channel"""
        m1 = MP3MetaData.from_video(
            title="Castaway",
            channel="Chasen - Topic",
        )
        self.assertEqual(m1.title, "Chasen - Castaway")

    def test_fix_title_strings_to_remove(self):
        """Tests that on initialization, the title removes specific strings"""
        m1 = MP3MetaData.from_video(
            "My Chemical Romance - Dead! Lyrics",
            "Muzic303",
        )
        self.assertEqual(m1.title, "My Chemical Romance - Dead!")

        m2 = MP3MetaData.from_video(
            "My Chemical Romance - Dead! Lyrics 1080p (mega official video by Muzic303)",
            "Muzic303",
        )
        self.assertEqual(m2.title, "My Chemical Romance - Dead!")


if __name__ == "__main__":
    unittest.main()
