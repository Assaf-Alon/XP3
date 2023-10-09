# METADATA SCHEME:
https://musicbrainz.org/doc/MusicBrainz_Database/Schema

# Changes
- [x] Use logger instead of prints  
- [x] Call fix_title on init. Remove the function  
- [x] Remove title, work with band & song only (title can be accessed via getters)  
- [ ] Catch errors on relevant operations (try except)  
- [ ] Raise errors instead of assert  
- [ ] Change pick  
- [ ] Multiple constructors, with @classmethod maybe (from_file, from_video)  
- [ ] Special cases for artists (eg. DECO*27) - to dictionary instead of convert_[to/from]  _filename
- [ ] Special cases for title strings (strings_to_remove) - to dictionary  
- [ ] Add `get_artwork_path` function (handle cases of singles and such)  

# Upgrades
- [ ] Address API Scheme to improve query (be able to get data for Linkin Park - Papercut (album = Hybrid Theory) and Foo Fighters - I'll Stick Around (album = Foo Fighters)). Main issue stems from the fact that these songs were first released as singles.
- [ ] When updating files, try to read existing metadata and suggest to use it (to just update the album artwork)  
- [ ] update_metadata_from_path - instead of just doing `song = Song(title=song_title)`, try to read existing metadata, and possibly exit early. Add `override` parameter to ignore metadata  
- [ ] Check if can swap band and song [Papercut - Linkin Park] (via API calls?)  

# Tests
- [x] Test mp4 download  
- [x] Test image download  
- [ ] Test mp4 to mp3 convertion  
- [ ] Test the metadata update  

# Feature Requests
- [ ] Filter out 'Greatest Hits'  
- [ ] Conflict handling - if ran before and configured (album, track), notify if the current song is also in (album, track)  