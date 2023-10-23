# pylist: Your Music Downloader and Playlist Organizer

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
- [Contributing](#contributing)

## About

`pylist` is designed as a tool to aid in downloading and organizing your music playlists. Whether you're a DJ looking for a simple way to manage tracks or someone who enjoys curating personal playlists, `pylist` has something to offer. Please note that this tool is created for **educational purposes only**.

## Features

- Download tracks from YouTube playlists
- Organize your playlists with ease
- Command-line and graphical interfaces
- Add metadata to MP3 files

## Installation

### Prerequisites

- Python 3.x
- pip

### Installing via PyPI

To install `pylist`, open your terminal and run the following command:

```bash
pip install pylist
```

## Usage

### Command-line Interface

To use `pylist` from the command line, you can utilize various options as shown below:

```bash
pylist -d <destination_directory> <youtube_playlist_url> [-g <genre>]
```

Here, `-d` specifies the directory where the files will be saved, and `-g` is used to specify the genre of the songs. The YouTube playlist URL is a required argument.

For example:

```bash
pylist -d ~/Music/MyPlaylist https://www.youtube.com/playlist?list=PLxxxxxx -g "Pop"
```

### Graphical User Interface

If you prefer using a graphical interface, you can run:

```bash
pylist-gui
```

This will open the graphical user interface where you can download and organize your music.

## Disclaimer

This tool is intended for educational purposes only. Downloading copyrighted music without authorization infringes upon the rights of the artists and content creators. If you like a track, we strongly recommend purchasing it to support the artists.

## License

MIT License. See `LICENSE` for more information.

## Contributing

We welcome contributions! Please read our `CONTRIBUTING.md` file for guidelines on how to contribute.
