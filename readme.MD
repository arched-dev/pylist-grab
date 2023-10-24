# pylist-grab: Your Music Downloader and Playlist Organizer

> 🎵 A Python-based utility for downloading and organising your playlists. Built for educational purposes.

## Table of Contents

- [About](#about)
- [Features](#features)
- [Installation](#installation)
  - [Prerequisites (linux)](#prerequisites)
  - [Installing via PyPI](#installing-via-pypi)
  - [Installing on Windows](#installing-on-windows)
- [Usage](#usage)
  - [Command-line Interface](#command-line-interface)
  - [Graphical User Interface](#graphical-user-interface)
- [Disclaimer](#disclaimer)
- [License](#license)

## About

# pylist-grab

`pylist-grab` is a comprehensive CLI and GUI tool designed to make your music management experience hassle-free and efficient. With just a few simple commands or clicks, you can download an entire YouTube playlist as MP3 files, complete with accurate filenames and rich metadata, including artwork, genre, artist, and more.

## Why Choose pylist-grab?

### Time-Saving
Gone are the days of downloading tracks one at a time from YouTube via online services. `pylist-grab` allows you to grab an entire playlist in one go, saving you both time and effort.

### Rich Metadata
Most online YouTube to MP3 converters do a poor job of preserving track metadata. `pylist-grab` stands apart by not just downloading the tracks but also by populating the metadata fields. This includes the artwork, genre, artist name, and other ID3 tags, which are crucial for music organization.

### Ideal for DJs and Music Enthusiasts
If you're a DJ, you know how important it is to have your music library organised. Missing or incorrect metadata can create a chaotic experience when you're trying to quickly find the right track during a live set. `pylist-grab` fills this gap by ensuring that each downloaded MP3 file is tagged correctly, allowing you to sort, filter, and search your music effortlessly in your DJ software.

### User-Friendly Interface
Whether you're comfortable with command lines or prefer a GUI, `pylist-grab` has got you covered. The CLI version is powerful and flexible, while the GUI version provides an easy-to-use interface for those who are not as tech-savvy.

## Legal and Ethical Use
`pylist-grab` is developed solely for educational and demonstration purposes. It is crucial to understand that downloading copyrighted music without proper authorization violates copyright laws and deprives artists of their due earnings. We do not condone, endorse, or encourage the illegal downloading, redistribution, or financial exploitation of copyrighted material. If you appreciate an artist's work, we strongly urge you to support them through legal means, such as purchasing their music.

## Installation

### Prerequisites (linux)

- Python 3.x
- pip

### Installing via PyPI

To install `pylist-grab` in linux, open your terminal and run the following command:

```bash
pip install pylist-grab
```
### Installing on Windows

Download the fully compiled `pylist-grab.exe` and run. 
[Download pylist-grab.exe here](https://github.com/lewis-morris/pylist-grab/releases/download/v0.0.3/pylist-grab.exe)


## Usage

### Command-line Interface

To use `pylistgrab` from the command line, you can utilise various options as shown below:

```bash
pylistgrab -d <destination_directory> <youtube_playlist_url> [-g <genre>]
```

Here, `-d` specifies the directory where the files will be saved, and `-g` is used to specify the genre of the songs. The YouTube playlist URL is a required argument.

For example:

```bash
pylistgrab -d ~/Music/MyPlaylist https://www.youtube.com/playlist?list=PLxxxxxx -g "Pop"
```

### Graphical User Interface

If you prefer using a graphical interface, you can run:

```bash
pylistgrab-gui
```

This will open the graphical user interface where you can download and organise your music.

## Disclaimer

This tool is intended strictly for educational and demonstration purposes. By using `pylist-grab`, you assume full responsibility for any legal or ethical repercussions that may arise from its use or misuse. We expressly disclaim any liability for the unauthorised use of this tool and do not condone the unlawful downloading, redistribution, or financial gain from artists' copyrighted material. Should you choose to use this tool, you do so at your own risk, acknowledging that it is your responsibility to comply with all applicable laws.
## License

MIT Licence. See `LICENSE` for more information.
