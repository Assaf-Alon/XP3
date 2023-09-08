# Changes
[V] Use logger instead of prints
[] Catch errors on relevant operations (try except)
[] Raise errors instead of assert
[] Change pick
[] Call fix_title on init. Remove the function, remove band & song, work with title only (band & song can be accessed via getters and setters)
[] Special cases for artists (eg. DECO*27) - to dictionary instead of convert_[to/from]_filename
[] Special cases for title strings (strings_to_remove) - to dictionary

# Upgrades
[] When updating files, try to read existing metadata and suggest to use it (to just update the album artwork)
[] update_metadata_from_path - instead of just doing `song = Song(title=song_title)`, try to read existing metadata, and possibly exit early. Add `override` parameter to ignore metadata
[] Check if can swap band and song [Papercut - Linkin Park] (via API calls?)

# Tests
[] Actual tests that test the metadata update

