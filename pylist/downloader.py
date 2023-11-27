import os
import re
import time
from typing import Optional

import requests
from moviepy.editor import AudioFileClip
from mutagen.id3 import TCON, TALB
# Function to set metadata for MP3 files
from mutagen.id3 import TIT2, TPE1, COMM, APIC, TDRC
from mutagen.mp3 import MP3
from pylist.utils import run_silently
from pytube import Playlist, YouTube

invalid_characters_replacements = {
    "<": "_",  # Less than
    ">": "_",  # Greater than
    ":": "-",  # Colon
    "\"": "'", # Double quote
    "/": "-",  # Forward slash
    "\\": "-", # Backslash
    "|": "-",  # Vertical bar or pipe
    "?": "",   # Question mark
    "*": "",   # Asterisk
}
REMOVE_WORDS = [
    "|",
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
    "Clip Officile",
    "Clip Officiel",
    "Official",
    "Official",
    "HD",
    "HD",
    "[HQ]",
    "HQ"
    "4K",
    "[HD]",
    "4K",
    "VEVO",
    "VEVO",
    "Explicit",
    "Explicit",
    "Music Video",
    "(Clean)",
    "Demo",
    "Demo",
    "Teaser",
    "Teaser",
    "Performance Video",
    "Performance Video",
]


# Function to set metadata for MP3 files


def set_metadata(
        save_path: str,
        filename: str,
        author: str,
        title: str,
        album: str,
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
        album (str),  The album name
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
        audio.save()
        audio = MP3(save_path)

    if author:
        audio["TPE1"] = TPE1(encoding=3, text=author)
        audio.save()
        audio = MP3(save_path)

    if album:  # Set the album name
        audio["TALB"] = TALB(encoding=3, text=album)
        audio.save()
        audio = MP3(save_path)

    if comment:
        audio["COMM"] = COMM(encoding=3, lang="eng", desc="desc", text=comment)
        audio.save()
        audio = MP3(save_path)

    if date:
        audio["TDRC"] = TDRC(encoding=3, text=str(date))  # Setting the release date
        audio.save()
        audio = MP3(save_path)


    # Add featured artist if provided
    featured_artist = grab_ft(title)
    if featured_artist:
        featured_artist_tag = TPE1(encoding=3, text=featured_artist)
        if "TPE2" in audio:
            audio["TPE2"].text[0] = featured_artist
            audio.save()

        else:
            audio["TPE2"] = featured_artist_tag
            audio.save()
        audio = MP3(save_path)


    # Download and add artwork
    if artwork:
        artwork = requests.get(artwork).content
        audio.tags.add(
            APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=artwork)
        )
        audio.save()

    # Add genre if provided
    if genre:
        audio["TCON"] = TCON(encoding=3, text=genre)
        audio.save()


def clean_remix(title, author):
    """
    Clean the title of the song
    """
    if author in title:
        title.replace(title, "")
    if "()" in title:
        title.replace("()", "")
    for type in ["bootleg", "remix", "edit", "mix", "rework", "re-edit"]:
        if f"({type})" in title.lower():
            title.replace(f"({type})", "type")

    return title
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
        .replace("( ", "(")
        .replace(" )", ")")
        .replace("/", " - ")
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


def download_stream_from_url(song_url: str):
    """
    Download the audio stream from the YouTube video
    Args:
        song_url (str): The URL of the YouTube video

    Returns:
        YouTube: The YouTube object
    """
    # Get the audio stream with the highest bitrate
    yt = YouTube(song_url)
    audio_stream = yt.streams.filter(only_audio=True).order_by("abr").desc().first()
    audio_stream.download(filename="temp_audio", max_retries=5)
    return yt


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

def pull_genre(title):
    options = ["Deep House", "Electro House", "Future House", "Progressive House", "Tech House", "Tropical House", "Techno", "Detroit Techno", "Minimal Techno", "Dub Techno", "Industrial Techno", "Drum and Bass", "Liquid Drum and Bass", "Jump-Up", "Neurofunk", "Jungle", "Dubstep", "Brostep", "Chillstep", "Trance", "Progressive Trance", "Psytrance (Psychedelic Trance)", "Vocal Trance", "Uplifting Trance", "Electro", "Electroclash", "Electropop", "EDM", "Big Room", "Dance-Pop", "Ambient", "Ambient House", "Dark Ambient", "Drone Music", "Breakbeat", "Nu Skool Breaks", "Big Beat", "Breakcore", "Hardcore", "Happy Hardcore", "Gabber", "UK Hardcore", "Industrial", "EBM", "Aggrotech", "IDM", "Glitch", "Drill 'n' Bass", "Trip-Hop", "Downtempo", "Glitch Hop", "Moombahton", "Future Bass", "Grime", "Trap", "Hybrid Trap", "Synthwave", "Vaporwave", "Outrun", "Chillwave", "House",  "DnB", "Drum & Bass", "Drum & base",  ]
    for op in options:
        if op.lower() in title.lower():
            return op
def attempt_get_title_author(yt: YouTube):
    """
    Attempt to get the title and author from the YouTube object
    """
    try:
        author, title = yt.title.split("-")
    except:
        parts = yt.title.split("-")
        author = parts[0]
        title = " ".join(parts[1:])

    return author, title

def pull_meta_data(yt: str):
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

        author, title = attempt_get_title_author(yt)
        title = title.strip().replace("  ", " ")
        author = author.strip().replace("  ", " ")
    else:
        author = yt.author
        title = yt.title

    title = clean_title(title, featured)
    author = clean_title(author, featured)
    title = clean_remix(title, author)


    if featured:
        author = f"{author}, {featured}"

    # Determine filename, author, and title
    if "-" not in title:
        filename = f"{title} - {author}"
    else:
        filename = title.replace("/", " ").replace("\\", " ")

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


def read_write_audio(meta_data: dict, dump_directory: str):
    """
    Convert the audio file to mp3 format
    Args:
        meta_data (dict): The metadata
        dump_directory (str): The directory to dump the file to

    Returns:
        filename (str): The name of the file
    """
    audio = AudioFileClip("temp_audio")
    save_filename = f"{meta_data['filename']}.mp3"
    final_save_filename = os.path.join(dump_directory, save_filename)
    audio.write_audiofile(final_save_filename)
    os.remove("temp_audio")
    return final_save_filename


def download_playlist(
        playlist: Playlist,
        dump_directory="./",
        genre: Optional[str] = None,
        do_yield=True,
        verbosity=1,
        download_indicator_function: Optional[callable] = None,
        silence=True,
):
    """
    Download a playlist from YouTube, song by song, adding the metadata thats extracted from the video

    Args:
        playlist (Playlist): The playlist object
        dump_directory (str): The directory to dump the files to
        genre (str): The genre of the songs
        do_yield (bool): Whether to yield the metadata
        verbosity (int): The verbosity level  0 to 2. 0 is no output, 1 is minimal output, 2 is full output
        download_indicator_function (callable): A function to call to indicate that a download has started
        silence (bool): Whether to silence the output
    """

    def log(message, indicator: Optional[callable] = None, no_indicator: Optional[int] = 0):
        """
        Log a message
        Args:
            message (str): The message to log
            indicator (callable): A function to call to indicate that a download has started
            no_indicator (int): The status from 0 to x
        """
        if verbosity > 1:
            print(message)
        if indicator:
            indicator(no_indicator)

    if dump_directory and not os.path.exists(dump_directory):
        raise Exception("Dump directory does not exist")

    # Loop through all videos in the playlist
    for url in playlist.video_urls:
        for attempt in range(5):
            try:
                start_time = time.time()

                log("Attempting to grab: " + url, download_indicator_function, 1)
                yt = run_silently(download_stream_from_url, silence, url)
                if yt:
                    meta_data = pull_meta_data(yt)
                    log("Metadata received: " + str(meta_data))

                    log("Attempting to download")
                    filename = run_silently(read_write_audio, silence, meta_data, dump_directory)

                    log("Download complete", download_indicator_function, 2)

                    run_silently(set_metadata, silence, save_path=filename, genre=genre, **{**meta_data, **{"album":playlist.title}})
                    log("MP3 Metadata saved")

                    end_time = time.time()
                    time_taken = (
                            end_time - start_time
                    )  # Time taken for this download in seconds

                    if do_yield:
                        yield meta_data, time_taken
                        break
                    log("Download complete", download_indicator_function, 3)
                else:
                    if verbosity > 0:
                        log("Could not download: " + url)


            except Exception as e:
                if verbosity > 0:
                    log(f"Could not download: {url} because of {e}")
                if attempt == 4:
                    yield None, None
