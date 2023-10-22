import argparse
from downloader import download_playlist, validate_playlist


def main():
    parser = argparse.ArgumentParser(
        description="Download a YouTube playlist and add metadata to MP3 files."
    )
    parser.add_argument(
        "-d", "--dump-dir", required=True, help="Directory to dump the files to"
    )
    parser.add_argument("-g", "--genre", help="Genre of the songs")
    parser.add_argument("url", help="YouTube playlist URL")

    args = parser.parse_args()

    playlist_url = args.url
    dump_directory = args.dump_dir
    genre = args.genre

    playlist = validate_playlist(
        playlist_url
    )  # Implement this function to get a Playlist object
    for meta_data in download_playlist(playlist, dump_directory, genre):
        print("Downloaded:", meta_data["title"])


if __name__ == "__main__":
    main()
