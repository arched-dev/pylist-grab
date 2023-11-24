import logging
import sys
import os

def setup_logger():
    log_file_path = os.path.join(sys._MEIPASS, "application.log") if getattr(sys, 'frozen', False) else "application.log"
    logging.basicConfig(
        level=logging.ERROR,
        format="%(asctime)s [%(levelname)s]: %(message)s",
        handlers=[
            logging.FileHandler(log_file_path),
            logging.StreamHandler(sys.stderr)
        ]
    )

# Run the setup function to configure the logger
setup_logger()
