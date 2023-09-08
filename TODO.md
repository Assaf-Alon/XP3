
[] When updating files, try to read existing metadata and suggest to use it (to just update the album artwork)
[] Catch errors (try except)
[] Use logger instead of prints
[] Actual tests that test the metadata update
[] Change pick
[] Check if can swap band and song [Papercut - Linkin Park] (via API calls?)
[] Raise errors instead of assert
[] Add "title_veritifed" field and update it after fix_title
[] Change some prints to logging
[] assert self.band and (self.album or self.song)  # TODO - standardize this (via title_verified)
[] update_metadata_from_path - instead of just doing `song = Song(title=song_title)`, try to read existing metadata, and possibly exit early. Add `override` parameter to ignore metadata
 