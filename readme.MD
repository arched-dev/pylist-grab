# pylist-grab: Your Music Downloader and Playlist Organizer

> 🎵 A Python-based utility for downloading and organizing your playlists. Built for educational purposes.

## Table of Contents

- [About](#about)
- [Features](#features)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Installing via PyPI](#installing-via-pypi)
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
If you're a DJ, you know how important it is to have your music library organized. Missing or incorrect metadata can create a chaotic experience when you're trying to quickly find the right track during a live set. `pylist-grab` fills this gap by ensuring that each downloaded MP3 file is tagged correctly, allowing you to sort, filter, and search your music effortlessly in your DJ software.

### User-Friendly Interface
Whether you're comfortable with command lines or prefer a GUI, `pylist-grab` has got you covered. The CLI version is powerful and flexible, while the GUI version provides an easy-to-use interface for those who are not as tech-savvy.

## Legal and Ethical Use
It's important to note that `pylist-grab` is intended for educational purposes only. Downloading copyrighted music without authorization violates the musician's copyright, and we strongly encourage you to support the artists by purchasing their music legally. 

By choosing `pylist-grab`, you're not just opting for convenience; you're choosing a robust, feature-rich solution that respects the art of music organization as much as you do.
## Installation

### Prerequisites (linux)

- Python 3.x
- pip

### Installing via PyPI

To install `pylist-grab` in linux, open your terminal and run the following command:

```bash
pip install pylist-grab
```
### Running in Windows

Download the fully compiled `pylist-grab.exe` and run. 

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

This will open the graphical user interface where you can download and organize your music.

## Disclaimer

This tool is intended for educational purposes only. Downloading copyrighted music without authorization infringes upon the rights of the artists and content creators. If you like a track, we strongly recommend purchasing it to support the artists.

## License

MIT License. See `LICENSE` for more information.
