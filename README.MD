# XP3 - Easily Update MP3 Metadata

[![CI/CD](https://github.com/Assaf-Alon/XP3/actions/workflows/lint-and-test.yaml/badge.svg)](https://github.com/Assaf-Alon/XP3/actions/workflows/lint-and-test.yaml)

## Overview
This project is meant to enable easy and automated changes to the metadata of mp3 files with partial or no data.  
One of the base assumptions is that the name of the file is in the following format: `<artist> - <title>.mp3`.  

## Usage
Some common examples are described below

### Updating metadata for a single file
```python
from mp3_metadata import MP3MetaData
file_path = "/example/path/song.mp3"
metadata = MP3MetaData.from_file(file_path)
metadata.update_missing_fields()
metadata.update_album_art()
metadata.apply_on_file(file_path)
```
> Note that you can use the `interactive` flag on the `update` methods and choose manually the correct metadata out of the options

### Updating metadata for all mp3 files in directory 
```python
from mp3_metadata import update_metadata_for_directory
dir_path = "/example/path"
update_metadata_for_directory(dir_path)
```
