import argparse
import os
import sys
from datetime import timedelta
from pathlib import Path

try:
    from downloader import validate_playlist, download_playlist, download_playlist_threaded
except ImportError:
    from pylist.downloader import validate_playlist, download_playlist


class CustomArgParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write("error: %s\n" % message)
        self.print_help()
        sys.stderr.write("\nFor example, you can use the following command:\n")
        sys.stderr.write(
            "cli.py -d <destination_directory> <youtube_playlist_url> [-g <genre>]\n"
        )
        sys.exit(2)


def print_progress_bar(completed, total, author, title, avg_time_per_item, bar_length=50):
    progress = float(completed) / float(total)
    arrow = "=" * int(round(progress * bar_length) - 1)
    spaces = " " * (bar_length - len(arrow))

    remaining_items = total - completed
    estimated_time_left = avg_time_per_item * remaining_items
    estimated_time_str = str(timedelta(seconds=round(estimated_time_left)))

    sys.stdout.write(
        f"\r[{arrow}{spaces}] {int(progress * 100)}% Complete ({completed}/{total} ~{estimated_time_str} left) - Latest Download: {author} - {title}                                          "
    )
    sys.stdout.flush()


def confirm_dump_dir():
    """
    If no dump directory is supplied, ask the user for confirmation to use the default directory.
    """

    # Determine the platform-specific desktop directory
    desktop = str(Path.home() / "Desktop")
    default_directory = os.path.join(desktop, "Youtube_MP3_dump")

    # Ask for user confirmation
    confirmation = input(
        f"No dump directory supplied. Do you want to save files to the default directory: {default_directory}? [y/n] "
    ).lower()

    if confirmation == "y":
        dump_directory = default_directory
        # Create the directory if it doesn't exist
        if not os.path.exists(dump_directory):
            os.makedirs(dump_directory)
    else:
        print("Operation cancelled.")
        return

    return dump_directory



def return_get_cli_args():
    """
    Returns a function that parses the command line arguments.

    """
    parser = CustomArgParser(
        description="Download a YouTube playlist and add metadata to MP3 files."
    )
    parser.add_argument(
        "-d", "--dump-dir", required=False, help="Directory to dump the files to"
    )
    parser.add_argument("-g", "--genre", required=False, help="Genre of the songs")
    parser.add_argument("url", help="YouTube playlist URL")

    return parser.parse_args()

def main():

    args = return_get_cli_args()  # Get the command line arguments

    playlist_url = args.url
    dump_directory = args.dump_dir
    genre = args.genre

    if dump_directory is None:
        dump_directory = confirm_dump_dir()


    playlist = validate_playlist(playlist_url)
    total_songs = len(playlist)

    total_time_taken = 0

    for i, data in enumerate(download_playlist(playlist, dump_directory, genre, silence=True)):
        if "metadata" in data:
            song_meta = data["metadata"]
            time_taken = data["time_taken"]
        else:
            song_meta, time_taken = data

        total_time_taken += time_taken
        avg_time_per_item = total_time_taken / (i + 1)

        print_progress_bar(
            i + 1,
            total_songs,
            song_meta["author"],
            song_meta["title"],
            avg_time_per_item,
        )

    print("\nDownloads complete.")


if __name__ == "__main__":
    main()
