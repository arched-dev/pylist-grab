import io
import os
import platform
import re
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from queue import Queue
from typing import Optional, Generator, Dict, Any, Callable

import requests
from moviepy.editor import AudioFileClip
from mutagen.id3 import TCON
# Function to set metadata for MP3 files
from mutagen.id3 import TIT2, TPE1, COMM, APIC, TDRC
from mutagen.mp3 import MP3
from pytube import Playlist, YouTube
import logging

try:
    from pylist.logging_config import setup_logger  # This line configures your logger
    from pylist.utils import run_silently, sanitize_filename
except ImportError:
    from logging_config import setup_logger  # This line configures your logger
    from utils import run_silently, sanitize_filename

IS_WINDOWS_EXE = hasattr(sys, '_MEIPASS')

REMOVE_WORDS = [
    "Official Video",
    "Official Video",
    "Lyric Video",
    "Lyric Video",
    "Official Music Video",
    "Official Music Video",
    "Official Lyric Video",
    "Official Audio",
    "Official Audio",
    "Visualizer",
    "Visualizer",
    "Audio",
    "Audio",
    "Cover",
    "Cover",
    "MV",
    "MV",
    "Extended Version",
    "Extended Version",
    "Instrumental",
    "Radio Edit",
    "Radio Edit",
    "Clip Officiel",
    "Clip Officiel",
    "Official",
    "Official",
    "HD",
    "HD",
    "4K",
    "4K",
    "VEVO",
    "VEVO",
    "Explicit",
    "Explicit",
    "(Clean)",
    "Demo",
    "Demo",
    "(FREE)",
    "Teaser",
    "Teaser",
    "Performance Video",
    "Performance Video",
]


def set_metadata(
        save_path: str,
        filename: str,
        author: str,
        title: str,
        artwork: str,
        keywords: str,
        comment: str,
        date: str,
        genre: Optional[str] = None,
):
    """
    Set the metadata for the MP3 file
    Args:
        save_path (str): The path to save the file to
        filename (str): The name of the file
        author (str): The author of the song
        title (str): The title of the song
        artwork (str): The URL of the artwork
        keywords (str): The keywords
        comment (str): The comment
        date (str): The date

    Returns:
        None

    """
    audio = MP3(save_path)

    # Add ID3 tag if it doesn't exist
    try:
        audio.add_tags()
    except Exception as e:
        print(f"Could not add tags: {e}")

    if title:
        audio["TIT2"] = TIT2(encoding=3, text=title)
    if author:
        audio["TPE1"] = TPE1(encoding=3, text=author)
    if comment:
        audio["COMM"] = COMM(encoding=3, lang="eng", desc="desc", text=comment)
    if date:
        audio["TDRC"] = TDRC(encoding=3, text=str(date))  # Setting the release date

    # Add featured artist if provided
    featured_artist = grab_ft(title)
    if featured_artist:
        featured_artist_tag = TPE1(encoding=3, text=featured_artist)
        if "TPE2" in audio:
            audio["TPE2"].text[0] = featured_artist
        else:
            audio["TPE2"] = featured_artist_tag

    # Download and add artwork
    if artwork:
        artwork = requests.get(artwork).content
        audio.tags.add(
            APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=artwork)
        )
    # Add genre if provided
    if genre:
        audio["TCON"] = TCON(encoding=3, text=genre)

    audio.save()


def clean_title(title: str, featured: str):
    """
    Clean the title of the song
    Args:
        title (str): The title of the song
        featured (str): The featured artist
    """
    for word in REMOVE_WORDS:
        title = (
            title.replace(word, "")
            .replace(word.lower(), "")
            .replace(word.upper(), "")
            .replace(word.title(), "")
        )

    title = title.replace(featured, "").replace("(ft. )", '').replace("ft. ", '').replace("ft ", '')

    return (
        title.replace("  ", " ")
        .replace("()", "")
        .replace("[]", "")
        .replace("( )", "")
        .replace("[ ]", "")
        .replace("  ", " ")
        .strip()
    )


def grab_ft(title: str):
    """
    Grab the ft. part of the title which would be the featured artist
    Args:
        title (str): The title of the song

    Returns:
        str: The featured artist
    """
    if "ft" in title.lower():
        location = title.lower().find("ft")
        return title[location:].strip()


# Initialize a Playlist object


def validate_playlist(playlist_url: str):
    """
    Validate the playlist URL and return the playlist object
    Args:
        playlist_url (str): The URL of the playlist

    Returns:

    """
    playlist = Playlist(playlist_url)

    if len(playlist.video_urls) == 0:
        raise Exception("Playlist is empty")

    return playlist


def remove_and_return_bootleg_remix(input_str):
    # Regex pattern to find '(xxxxx bootleg)' or '(xxxxx remix)', case insensitive
    pattern = r"\((.*? bootleg)\)|\((.*? remix)\)"

    # Search for the pattern
    match = re.search(pattern, input_str, re.IGNORECASE)

    if match:
        # Found the pattern, remove it from the string
        found_text = match.group().strip('()')
        cleaned_str = re.sub(pattern, "", input_str, flags=re.IGNORECASE).strip()
        return cleaned_str, found_text
    else:
        # Pattern not found, return original string and None
        return input_str, None


def extract_featured_artist(song_info):
    # Regular expression to capture artist name after 'ft.'
    # This pattern accounts for optional parentheses, and considers different placements of 'ft.'
    regex_patterns = [
        r'ft\.\s*(?:\()?(.*?)(?:\))?\s*-',  # Before the dash
        r'-\s*(?:.*?)ft\.\s*(?:\()?(.*?)(?:\))?$'  # After the dash
    ]

    for pattern in regex_patterns:
        # Perform regex search
        match = re.search(pattern, song_info)
        if match:
            return match.group(1).strip()

    return None


def pull_meta_data(yt: YouTube) -> Dict[str, Any]:
    """
    Pull metadata from the YouTube video
    Args:
        yt (YouTube): The YouTube object

    Returns:
        dict: The metadata
    """
    featured = extract_featured_artist(yt.title) if extract_featured_artist(yt.title) else extract_featured_artist(
        yt.author)
    if featured is None:
        featured = ''

    if "-" in yt.title:
        author, title = yt.title.split("-")
        title = title.strip().replace("  ", " ")
        author = author.strip().replace("  ", " ")
    else:
        author = yt.author
        title = yt.title

    title, extra_artist = remove_and_return_bootleg_remix(title)

    title = clean_title(title, featured)
    author = clean_title(author, featured)

    if featured:
        author = f"{author} ft. {featured}"
    if extra_artist:
        author = f"{author} ({extra_artist})"

    # Determine filename, author, and title
    if "-" not in title:
        filename = f"{title} - {author}"
    else:
        filename = title

    # Additional metadata
    artwork = yt.thumbnail_url
    keywords = yt.keywords
    comment = yt.description
    date = yt.publish_date

    return {
        "filename": filename,
        "author": author,
        "title": title,
        "artwork": artwork,
        "keywords": keywords,
        "comment": comment,
        "date": date,
    }


def pull_audio_and_meta_data(url: str, dump_directory: str) -> Dict[str, Any]:
    """Pull meta data from a youtube url."""
    # Existing meta data extraction logic
    with tempfile.TemporaryDirectory() as temp_dir:

        yt = YouTube(url)
        meta_data = pull_meta_data(yt)
        audio_stream = yt.streams.filter(only_audio=True).first()

        temp_save_path = audio_stream.download(output_path=temp_dir)
        logging.debug(f"temp_save_path: {temp_save_path}")

        final_save_path = os.path.join(dump_directory, sanitize_filename(meta_data["filename"] + ".mp3"))

        audio = None
        try:
            if os.path.isfile(temp_save_path) and os.path.isdir(os.path.split(final_save_path)[0]):
                audio = AudioFileClip(temp_save_path)
                audio.write_audiofile(final_save_path, write_logfile=False, logger=None, verbose=False)
            else:
                logging.error("Either the temp_save_path is not a file or the final_save_path is not a directory")
        except Exception as e:
            logging.error("Failed to process audio")
            logging.error(str(e), exc_info=True)

        if hasattr(audio, "close"):
            audio.close()

        # Temp files will be deleted once we're out of the 'with' block
    return meta_data, final_save_path


def process_single_video(url: str, dump_directory: str, genre: Optional[str], verbosity: int,
                         silence: Optional[bool]) -> Dict[str, Any]:
    """Process a single video URL and return the metadata and time taken."""
    try:
        start_time = time.time()

        if IS_WINDOWS_EXE:
            meta_data, final_save_path = pull_audio_and_meta_data(url, dump_directory)
            set_metadata(save_path=final_save_path, genre=genre, **meta_data)
        else:
            meta_data, final_save_path = run_silently(pull_audio_and_meta_data, silence, url, dump_directory)
            run_silently(set_metadata, silence, save_path=final_save_path, genre=genre, **meta_data)

        end_time = time.time()
        return {"metadata": meta_data, "time_taken": end_time - start_time, "error": None}
    except Exception as e:
        if verbosity > 0:
            logging.error(f"Could not download: {url} because of {e}")
        return {"metadata": None, "time_taken": None, "error": e}


def download_playlist(playlist: Playlist,
                      dump_directory: str = "./",
                      genre: Optional[str] = None,
                      do_yield: bool = True,
                      verbosity: int = 1,
                      download_indicator_function: Optional[Callable[[int], None]] = None,
                      silence: Optional[bool] = False) -> Generator[Dict[str, Any], None, None]:
    """Download a playlist from YouTube, song by song, adding the metadata extracted from the video."""
    if not os.path.exists(dump_directory):
        raise Exception("Dump directory does not exist")

    def log_message(message: str, indicator: Optional[Callable[[int], None]] = None, status: Optional[int] = 0):
        """Logs messages based on verbosity and calls an optional indicator function."""
        if verbosity > 1:
            logging.info(message)
        if indicator:
            indicator(status)

    for url in playlist.video_urls:
        log_message(f"Attempting to grab: {url}", download_indicator_function, 1)
        result = process_single_video(url, dump_directory, genre, verbosity, silence)
        if result["metadata"]:
            if do_yield:
                yield result
            log_message("Download complete", download_indicator_function, 3)
        else:
            if verbosity > 0:
                logging.error(f"Could not download: {url}")
