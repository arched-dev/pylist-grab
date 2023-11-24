import logging
import sys
import os
import re


def sanitize_filename(filename):
    """
    Sanitize a string to make it safe for use as a filename.

    Args:
        filename (str): The original filename string.

    Returns:
        str: A sanitized version of the filename string.
    """

    # Remove invalid characters
    filename = re.sub(r'[\\/*?:"<>|]', '', filename)

    # Replace spaces with underscores

    # Remove leading and trailing whitespaces
    filename = filename.strip()

    # Truncate long filenames
    max_length = 255  # Maximum filename length
    if len(filename) > max_length:
        filename = filename[:max_length]

    return filename


def run_silently(func, silence=True, *args, **kwargs):
    if silence:
        with open(os.devnull, 'w') as fnull:
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = sys.stderr = fnull

            try:
                return_value = func(*args, **kwargs)
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
            return return_value
    else:
        return func(*args, **kwargs)

log_file_path = os.path.join(sys._MEIPASS, "application.log") if getattr(sys, 'frozen', False) else "application.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler(sys.stderr)
    ]
)
