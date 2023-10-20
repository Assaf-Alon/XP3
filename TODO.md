# METADATA SCHEME:
https://musicbrainz.org/doc/MusicBrainz_Database/Schema

# Changes
- [x] Use logger instead of prints  
- [x] Call fix_title on init. Remove the function  
- [x] Remove title, work with band & song only (title can be accessed via getters)  
- [x] Multiple constructors, with @classmethod maybe (from_file, from_video)  
- [ ] Create an Album class instead of using 3-tuple.
- [ ] Catch errors on relevant operations (try except)  
- [ ] Raise errors instead of assert  
- [ ] Change pick  
- [ ] Special cases for artists (eg. DECO*27) - to dictionary instead of convert_[to/from]  _filename
- [ ] Special cases for title strings (strings_to_remove) - to dictionary  
- [ ] Add `get_artwork_path` function (handle cases of singles and such)  
- [ ] Add Docstrings to functions

# Upgrades
- [x] When updating files, try to read existing metadata and suggest to use it (to just update the album artwork)  
- [x] update_metadata_from_path - instead of just doing `song = Song(title=song_title)`, try to read existing metadata, and possibly exit early.
- [x] Update from directory - use conventions to avoid API calls (format is `ARTIST/ALBUM (YEAR)`)  
- [ ] Address API Scheme to improve query (be able to get data for Linkin Park - Papercut (album = Hybrid Theory) and Foo Fighters - I'll Stick Around (album = Foo Fighters)). Main issue stems from the fact that these songs were first released as singles.
- [ ] Check if can swap band and song [Papercut - Linkin Park] (via API calls?)  
- [ ] Add default to mp3_dir and mp4_dir, and in the program workflow check if it exists and create it it doesnt
- [ ] CICD
- [ ] Add more logging (debug)
- [ ] User interaction file (get_user_input, convert n/y to booleans and such...)

# Tests
- [x] Test mp4 download  
- [x] Test image download  
- [ ] Test singles that were later added to albums
- [ ] Test mp4 to mp3 convertion  
- [ ] Test the metadata update  
- [ ] Test extract_album_info_from_path 
- [ ] Test from_file (with paths such as `ARTIST/ALBUM (YEAR)`) 
- [ ] https://stackoverflow.com/questions/60837213/how-to-run-test-case-marked-unittest-skip-in-python
- [ ] Convert unittest to pytest

# Feature Requests
- [ ] Filter out 'Greatest Hits'  
- [ ] Conflict handling - if ran before and configured (album, track), notify if the current song is also in (album, track)  