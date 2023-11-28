# TODOs are currently stored here..

## [METADATA SCHEME](https://musicbrainz.org/doc/MusicBrainz_Database/Schema)


## UP NEXT
- [ ] Changes - Use tempfiles
- [ ] Tests - Avenged Sevenfold - Nightmare cover art
- [ ] Tests - Avenged Sevenfold - HTTK cover art
- [ ] Remove comments from GitHub workflow

## Changes
- [ ] Fix pylint low prio issues (C0103,W0511,R0902,R0913,E0611)
- [ ] Catch errors on relevant operations (try except)  
- [ ] Raise errors instead of assert  
- [ ] Change pick  
- [ ] Special cases for artists (eg. DECO*27) - to dictionary instead of convert_[to/from]  _filename
- [ ] Special cases for title strings (strings_to_remove) - to dictionary
- [ ] Change in metadata title --> fullTitle  
- [ ] Change in metadata band --> artist  
- [ ] Change in metadata song --> title  

## Upgrades
- [ ] Address API Scheme to improve query (be able to get data for Linkin Park - Papercut (album = Hybrid Theory) and Foo Fighters - I'll Stick Around (album = Foo Fighters)). Main issue stems from the fact that these songs were first released as singles.
- [ ] Check if can swap band and song [Papercut - Linkin Park] (via API calls?)  
- [ ] Add more logging (debug)
- [ ] Configure language for artists (e.g. DECO*27), and if English doesn't work for them (0 results from query) try translating (e.g. mannequin translates correctly https://musicbrainz.org/release-group/4710e0e0-e417-45b4-9cf3-7a9f22c69174. Also make sure Ilay Botner works https://musicbrainz.org/artist/f958a500-5111-4f8b-abd2-9b7f37f18179/recordings)
- [ ] Handle "BAND - Topic" channel name
- [ ] env var dev / prod

## Tests
- [ ] Test mp4 to mp3 convertion  
- [ ] Test the metadata update  
- [ ] Test extract_album_info_from_path 
- [ ] Test from_file (with paths such as `ARTIST/ALBUM (YEAR)`) 
- [ ] https://stackoverflow.com/questions/60837213/how-to-run-test-case-marked-unittest-skip-in-python
- [ ] Convert unittest to pytest  
- [ ] Check possibility to move patch to class level  
- [ ] Test interactive parts  
- [ ] Automate tests from existing files with verified metadata  

## Feature Requests
- [ ] Conflict handling - if ran before and configured (album, track), notify if the current song is also in (album, track)  

## etc
- [ ] Tests for weird cases (no album), make sure nothing crashes...
- [ ] Configure Workflows (Tests run on push)