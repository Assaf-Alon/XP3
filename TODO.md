# METADATA SCHEME:
https://musicbrainz.org/doc/MusicBrainz_Database/Schema

# Changes
- [x] Use logger instead of prints  
- [x] Call fix_title on init. Remove the function  
- [x] Remove title, work with band & song only (title can be accessed via getters)  
- [x] Multiple constructors, with @classmethod maybe (from_file, from_video)  
- [x] Fix pylint issues (pylint $(git ls-files '*.py'))
- [x] Create a ReleaseRecording class instead of using 3-tuple.
- [x] Add Docstrings to functions
- [ ] Fix pylint low prio issues (C0103,W0511,R0902,R0913,E0611)
- [ ] Catch errors on relevant operations (try except)  
- [ ] Raise errors instead of assert  
- [ ] Change pick  
- [ ] Special cases for artists (eg. DECO*27) - to dictionary instead of convert_[to/from]  _filename
- [ ] Special cases for title strings (strings_to_remove) - to dictionary  
- [ ] Add `get_artwork_path` function (handle cases of singles and such)  

# Upgrades
- [x] When updating files, try to read existing metadata and suggest to use it (to just update the album artwork)  
- [x] update_metadata_from_path - instead of just doing `song = Song(title=song_title)`, try to read existing metadata, and possibly exit early.
- [x] Update from directory - use conventions to avoid API calls (format is `ARTIST/ALBUM (YEAR)`)  
- [x] GitHub workflow for testing and linting
- [ ] Address API Scheme to improve query (be able to get data for Linkin Park - Papercut (album = Hybrid Theory) and Foo Fighters - I'll Stick Around (album = Foo Fighters)). Main issue stems from the fact that these songs were first released as singles.
- [ ] Check if can swap band and song [Papercut - Linkin Park] (via API calls?)  
- [ ] Add default to mp3_dir and mp4_dir, and in the program workflow check if it exists and create it it doesnt
- [ ] Add more logging (debug)
- [ ] User interaction file (get_user_input, convert n/y to booleans and such...)
- [ ] Configure language for artists (e.g. DECO*27), and if English doesn't work for them (0 results from query) try translating (e.g. mannequin translates correctly https://musicbrainz.org/release-group/4710e0e0-e417-45b4-9cf3-7a9f22c69174. Also make sure Ilay Botner works https://musicbrainz.org/artist/f958a500-5111-4f8b-abd2-9b7f37f18179/recordings)
- [ ] Handle "BAND - Topic" channel name
- [ ] 

# Tests
- [x] Test mp4 download  
- [x] Test image download  
- [x] Test singles that were later added to albums
- [ ] Test mp4 to mp3 convertion  
- [ ] Test the metadata update  
- [ ] Test extract_album_info_from_path 
- [ ] Test from_file (with paths such as `ARTIST/ALBUM (YEAR)`) 
- [ ] https://stackoverflow.com/questions/60837213/how-to-run-test-case-marked-unittest-skip-in-python
- [ ] Convert unittest to pytest

# Feature Requests
- [ ] Filter out 'Greatest Hits'  
- [ ] Conflict handling - if ran before and configured (album, track), notify if the current song is also in (album, track)  

# etc
- [ ] Tests for weird cases (no album), make sure nothing crashes...
- [ ] Configure Workflows (Tests run on push)