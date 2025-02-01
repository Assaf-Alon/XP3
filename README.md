# XP3 - Easily Update MP3 Metadata

[![CI/CD](https://github.com/Assaf-Alon/XP3/actions/workflows/lint-and-test.yaml/badge.svg)](https://github.com/Assaf-Alon/XP3/actions/workflows/lint-and-test.yaml)

## Overview
XP3 is a tool designed to simplify and automate the process of updating metadata for MP3 files. It uses an external API and various heuristics to select the best metadata from multiple options. The tool assumes that the MP3 file names follow the format: `<artist> - <title>.mp3`.

## Usage

### Installation
#### 1. Clone the repository:
```bash
git clone https://github.com/Assaf-Alon/XP3
```

#### 2. Install [ffmpeg](https://en.wikipedia.org/wiki/FFmpeg):

##### Windows
1. [Download ffmpeg](https://www.ffmpeg.org/download.html)
2. Extract the contents to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to the Path environment variable

##### Ubuntu
```bash
sudo apt-get install ffmpeg
```

### Updating Metadata

#### Single File
To update metadata for a single MP3 file:
```python
from mp3_metadata import update_metadata_for_file

file_path = "/example/path/artist - song.mp3"
update_metadata_for_file(file_path)
```

> [!TIP]
> Use the `interactive` flag to manually select the correct metadata from the options returned by the API.

#### Directory
To update metadata for all MP3 files in a directory:
```python
from mp3_metadata import update_metadata_for_directory

dir_path = "/example/path"
update_metadata_for_directory(dir_path)
```
