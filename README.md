# XP3 - Easily Update MP3 Metadata

[![CI/CD](https://github.com/Assaf-Alon/XP3/actions/workflows/lint-and-test.yaml/badge.svg)](https://github.com/Assaf-Alon/XP3/actions/workflows/lint-and-test.yaml)

## Overview
This project is meant to enable easy and automated changes to the metadata of mp3 songs files with partial or no metadata, using an external API and various heuristics to choose between multiple options returned from the API query.  
One of the base assumptions is that the name of the file is in the following format: `<artist> - <title>.mp3`.  

## Usage

### Installation
```bash
git clone https://github.com/Assaf-Alon/XP3
```

And install [ffmpeg](https://en.wikipedia.org/wiki/FFmpeg)
#### Windows
1. [Download ffmpeg](https://www.ffmpeg.org/download.html)
2. Extract content in `C:\ffmpeg`, and add to the Path environment variable the following path: `C:\ffmpeg\bin`

#### Ubuntu
```
sudo apt-get install ffmpeg
```

### Updating metadata for a single file
```python
from mp3_metadata import update_metadata_for_file
file_path = "/example/path/artist - song.mp3"
update_metadata_for_file(file_path)
```
> Note that you can use the `interactive` flag on the `update` function and choose manually the correct metadata out of the valid options returned by the API call.

### Updating metadata for all mp3 files in directory
```python
from mp3_metadata import update_metadata_for_directory
dir_path = "/example/path"
update_metadata_for_directory(dir_path)
```
