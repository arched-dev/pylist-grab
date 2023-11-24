import os
import subprocess
import sys
import threading
import time
import webbrowser

import PySide6
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QPixmap, QAction, QIcon, QFont
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QLabel,
    QProgressBar,
    QScrollArea,
    QMessageBox,
    QHBoxLayout,
    QMainWindow,
    QSizePolicy,
    QWizardPage,
    QWizard,
    QSplashScreen, QListWidget, QListWidgetItem,
)
from qt_material import apply_stylesheet

from pylist.downloader import (
    download_playlist,
    validate_playlist, pull_genre,
)  # Replace these imports with your actual functions


def get_file(path, filename):
    # Split the path by '/' and remove any empty strings
    split_path = [x for x in path.split("/") if x]
    # Determine the base path
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    alt_base = os.path.join(*os.path.split(base_path)[:-1])
    # Loop through the directory levels in reverse order
    for base in [base_path, alt_base]:
        path_one = os.path.join(base, *split_path, filename)
        path_two = os.path.join(base, split_path[0], filename)
        path_three = os.path.join(base, split_path[1], filename)
        for check_path in [
            path_one,
            path_two,
            path_three,
        ]:  # Check if the file exists in the current path
            if os.path.exists(check_path):
                return check_path
    # Return None if the file was not found
    return None


ASSET_LOCATION = "/pylist/assets/"
IS_WINDOWS_EXE = hasattr(sys, "_MEIPASS")
WIZARD_TITLE = "How to Get a Valid YouTube Playlist URL"
WIZARD_PAGES = [
    {
        "text": "First, head over to YouTube and use the search bar to look for a genre or artist. Avoid searching for specific songs at this stage.",
        "image_path": get_file(ASSET_LOCATION, "page_1.png"),
    },
    {
        "text": "Once the search results are displayed, locate the 'Filter' button at the upper-right corner of the page. \n\nClick it and select 'Playlist' from the dropdown options.",
        "image_path": get_file(ASSET_LOCATION, "page_2.png"),
    },
    {
        "text": "Browse through the filtered results to find a playlist that catches your interest.\n\nEnsure that the thumbnail indicates multiple videos, or look for a listing that includes a 'VIEW FULL PLAYLIST' button. \n\nOpen the playlist you've chosen.",
        "image_path": get_file(ASSET_LOCATION, "page_3.png"),
    },
    {
        "text": "After the playlist page has loaded, you'll see a long list of videos on the right hand side of the page.\n\n You should see the playlist name at the top of this list, click on the 'playlist title' to view the playlist.",
        "image_path": get_file(ASSET_LOCATION, "page_4.png"),
    },
    {
        "text": "You should now be on the playlist's dedicated page. \n\n Verify this by checking if the URL starts with 'youtube.com/playlist?...'. \n\n This is the URL you need.",
        "image_path": get_file(ASSET_LOCATION, "page_5.png"),
    },
]


class HowToPage(QWizardPage):
    def __init__(self, text, image_path):
        super().__init__()
        layout = QVBoxLayout()

        # Create a QLabel for the text
        text_label = QLabel()
        text_label.setText(text)

        # Set the font size and add a border
        text_label.setFont(QFont("Arial", 14))  # Adjust the font size as needed
        text_label.setStyleSheet("QLabel { border: 2px solid black; padding: 10px; }")

        layout.addWidget(text_label)

        # Create a QLabel for the image
        image = QPixmap(image_path)
        image_label = QLabel()
        image_label.setPixmap(image)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center align the image
        image_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        layout.addWidget(image_label)
        self.setLayout(layout)


class HowToWizard(QWizard):
    def __init__(self, pages, title):
        super().__init__()
        self.setWindowTitle(title)

        for page_info in pages:
            text = page_info["text"]
            image_path = page_info["image_path"]
            self.addPage(HowToPage(text, image_path))


class App(QMainWindow):
    # download_progress = Signal(int, str, str, str, str, bool)
    temp_labels: list = []

    def __init__(self):
        super(App, self).__init__()
        self.playlist_length = 0
        self.initUI()

    def initUI(self):
        """
        Initialize the GUI.
        Returns:

        """

        self.output_folder = None

        self.create_menu()
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        # Add menu bar to main window

        url_layout = QHBoxLayout()

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter Playlist URL")
        self.url_input.editingFinished.connect(self.restore_placeholder)
        url_layout.addWidget(self.url_input)

        self.validate_url_button = QPushButton("Validate URL")
        self.validate_url_button.clicked.connect(self.validate_url)
        url_layout.addWidget(self.validate_url_button)

        layout.addLayout(url_layout)

        self.playlist_title = QLabel()
        self.playlist_title.setVisible(False)
        layout.addWidget(self.playlist_title)

        self.folder_button = QPushButton("Select Output Folder")
        self.folder_button.setEnabled(False)
        self.folder_button.clicked.connect(self.select_folder)
        self.output_location_label = QLabel()
        self.output_location_label.setText("No location selected")
        layout.addWidget(self.folder_button)
        layout.addWidget(self.output_location_label)

        if self.output_location_label == "" or self.output_location_label == "No location selected":
            self.download_button.setEnabled(False)

        self.genre = QLabel()
        self.genre.setText("Genre")
        self.genre_input = QLineEdit()
        self.genre_input.setPlaceholderText("Enter Genre")
        self.genre_input.setEnabled(False)
        layout.addWidget(self.genre)
        layout.addWidget(self.genre_input)


        #download_button

        self.song_list = QListWidget()
        self.song_list.setMinimumHeight(200)
        layout.addWidget(self.song_list)

        #stpp dowmloading
        self.download_button = QPushButton("Download List")
        self.download_button.clicked.connect(self.start_downloading)
        self.download_button.setEnabled(False)  # Enable only after downloads
        layout.addWidget(self.download_button)


        self.progress_label = QLabel("0/0")
        layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Set the layout to the central widget
        central_widget.setLayout(layout)

        self.setWindowTitle("MP3 Downloader")
        self.setMinimumWidth(500)

        # self.download_progress.connect(self.update_progress)
        self.show()

    def show_how_to(self):
        """
        Show the 'How to' wizard.
        Returns:

        """
        self.wizard = HowToWizard(WIZARD_PAGES, WIZARD_TITLE)
        self.wizard.show()

    def restore_placeholder(self):
        if not self.url_input.hasFocus() and not self.url_input.text():
            self.url_input.setPlaceholderText("Enter Playlist URL")

    def focusInEvent(self, event):
        self.url_input.setPlaceholderText("")

    def open_github(self):
        # Replace 'https://github.com/your_username/your_repository' with your actual GitHub repository URL
        github_url = "https://github.com/lewis-morris/pylist-grab"
        webbrowser.open(github_url)

    def create_menu(self):
        """
        Create the menu bar.
        Returns:
            None
        """
        menu_bar = self.menuBar()

        # Create top-level menu items
        file_menu = menu_bar.addMenu("File")
        view_menu = menu_bar.addMenu("View")
        about_menu = menu_bar.addMenu("About")

        # Create actions for File menu
        close_action = QAction("Close", self)
        close_action.triggered.connect(self.close_app)

        # Create actions for View menu
        what_it_does_action = QAction("What it does", self)
        what_it_does_action.triggered.connect(self.open_what_it_does)

        find_url_action = QAction("Finding playlist URL", self)
        find_url_action.triggered.connect(self.show_how_to)

        # Create actions for About menu
        about_action = QAction("About", self)
        about_action.triggered.connect(self.open_about_dialog)

        website_action = QAction("Website", self)
        website_action.triggered.connect(self.open_github)

        # Add actions to menus
        file_menu.addAction(close_action)
        view_menu.addAction(what_it_does_action)
        view_menu.addAction(find_url_action)
        about_menu.addAction(about_action)
        about_menu.addAction(website_action)

    def close_app(self):
        """
        Close the application.
        Returns:
            None
        """
        self.close()

    def open_what_it_does(self):
        """
        Open a dialog to display information about what the application does.
        Returns:
            None
        """
        msg = QMessageBox()
        msg.setWindowTitle("What it does")
        msg.setText(
            "This application enables you to download entire YouTube playlists in MP3 format while also populating the files with as much metadata as possible, including album artwork. \n\n"
            "While streaming services have largely rendered MP3s obsolete for the average listener, they remain essential for DJs and other professionals who need direct access to audio files.\n\nWell-formatted metadata makes it easier to manage your song catalog effectively.\n\nPlease note that this project serves as a proof of concept to demonstrate the technical feasibility of such a service. We do not endorse or encourage the unauthorized distribution of copyrighted material. Always remember to support your favorite artists by purchasing their music legally."
        )
        msg.exec()

    def open_about_dialog(self):
        """
        Open a dialog to display information about the application.
        Returns:
            None
        """
        msg = QMessageBox()
        msg.setWindowTitle("About")
        msg.setText(
            "GUI and cli interface & metadata injection written by Lewis Morris (lewis.morris@gmail.com)\n\n Libraries Used and Loved: \n\n pytube \n moviepy \n mutagen \n pyside6 \n qt_material"
        )
        msg.exec()

    def validate_url(self):
        """
        Validate the URL entered by the user, by checking if the playlist exists and returns results.

        Returns:
            None

        """
        url = self.url_input.text()
        try:
            self.playlist = validate_playlist(url)
            if self.playlist:
                self.folder_button.setEnabled(True)
                self.download_button.setEnabled(True)
                self.genre_input.setEnabled(True)
                self.playlist_length = len(self.playlist.video_urls)
                self.genre_input.setText(pull_genre(self.playlist.title))
                self.playlist_title.setText(self.playlist.title)
                self.playlist_title.setVisible(True)

        except Exception as e:
            error_dialog = QMessageBox(self)
            error_dialog.setWindowTitle("Invalid URL")
            error_dialog.setText(
                "The provided URL is invalid, you must provide a valid YouTube playlist URL. This will be in the format of https://www.youtube.com/playlist?..."
            )
            error_dialog.setIcon(QMessageBox.Icon.Warning)

            ok_button = error_dialog.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
            how_to_button = error_dialog.addButton(
                "Show me how", QMessageBox.ButtonRole.ActionRole
            )

            error_dialog.exec()

            if error_dialog.clickedButton() == how_to_button:
                self.show_how_to()

    def select_folder(self):
        """
        Open a file dialog to select the output folder.
        Returns:
            None
        """
        self.output_folder = QFileDialog.getExistingDirectory(
            self, "Select Output Folder"
        )
        if self.output_folder and os.path.isdir(self.output_folder):
            self.output_location_label.setText(self.output_folder)
            self.change_all(True)
        else:
            self.output_location_label.setText("Not a valid output folder")

    def change_all(self, status=False):
        """
        Change the enabled status of all widgets.
        Args:
            status (bool): The status to change to.

        Returns:
            None
        """
        self.download_button.setEnabled(status)
        self.genre_input.setEnabled(status)
        self.folder_button.setEnabled(status)
        self.validate_url_button.setEnabled(status)
        self.url_input.setEnabled(status)


    def toggle_downloading(self):
        if self.download_button.text() == "Start Downloading":
            self.start_downloading()
            self.download_button.setText("Stop Downloading")
            self.download_button.setEnabled(False)




    # @Slot(int, str, str, str, str, bool)
    def update_progress(
        self, i, artist, title, duration, estimated_remaining, download_started=False
    ):
        """
        Update the progress bar and the progress label.
        Args:
            i (int): The current index of the song being downloaded.
            artist (str): The artist of the song being downloaded.
            title (str): The title of the song being downloaded.
            duration (str): The duration of the song being downloaded.
            estimated_remaining (str): The estimated time remaining for the download.
            download_started (bool): Whether the download has started or not.

        Returns:
            None
        """
        print(f"update_progress called with {i}, {artist}, {title}")

        percent = int((i / self.playlist_length) * 100)
        self.progress_bar.setValue(percent)

        new_item = QListWidgetItem(f"{artist} - {title} (Download took: {duration})")
        new_item.setSizeHint(QSize(-1, 20))  # Adjust the height here
        self.song_list.insertItem(0, new_item)  # Add new item at the top

        # Automatically scroll to the newest item
        self.song_list.scrollToItem(new_item)

        if estimated_remaining:
            self.progress_label.setText(
                f"{i}/{self.playlist_length} (Estimated time remaining: {estimated_remaining})"
            )


    total_time = 0  # Total time taken for all songs in seconds

    def set_downloading(self, dots=0):
        """
        Update the download button text to indicate that the download is in progress.
        Args:
            dots (int): The number of dots to append to the text.

        Returns:
            None

        """
        self.download_button.setText("Downloading" + "." * dots)

    def validate_location(self):

        if self.output_folder is None:
            # Custom message box
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Save Location Error")
            msg_box.setText("You must first choose an save location. Generally this will be your 'Music' folder")
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            # Show the message box
            msg_box.exec()
            return False
        return True


    def start_downloading(self):
        """
        Start downloading the playlist, and update the GUI as the download progresses.
        Returns:

        """

        if self.validate_location() is True:
            self.change_all()
            self.set_downloading(0)

            self.total_time = 0  # Initialize total_time

            for i, (song_meta, time_taken) in enumerate(
                download_playlist(
                    self.playlist,
                    self.output_folder,
                    genre=self.genre_input.text(),
                    download_indicator_function=self.set_downloading,
                )
            ):
                title = song_meta["title"]
                artist = song_meta["author"]

                self.total_time += time_taken  # Updating the total time

                average_time = self.total_time / (i + 1)  # Average time per song
                estimated_remaining = average_time * (
                    self.playlist_length - (i + 1)
                )  # Estimate remaining time

                duration = time.strftime("%M:%S", time.gmtime(time_taken))
                estimated_remaining_str = time.strftime(
                    "%M:%S", time.gmtime(estimated_remaining)
                )

                self.update_progress(
                    i + 1, artist, title, duration, estimated_remaining_str, False
                )

                # self.download_progress.emit(i + 1, None, None, None, None, True)

                time.sleep(0.1)

            self.download_button.setText("Start Downloading")
            self.change_all(True)
        else:
            pass

    # def start_downloading(self):
    #     """
    #     Confirm that the user wants to start downloading the playlist, and start the download if they do.
    #     If a folder has not been selected, ask the user if they want to save the files to the default location.
    #     Returns:
    #         None
    #     """
    #     if not hasattr(self, "output_folder"):
    #         desktop = os.path.join(os.path.join(os.path.expanduser("~")), "Music")
    #         output_folder = os.path.join(desktop, "Youtube-rips")
    #
    #         confirm_dialog = QMessageBox(self)
    #         confirm_dialog.setWindowTitle("Confirm Folder")
    #         confirm_dialog.setText(
    #             f"You have not selected an output directory. Are you happy to save files to {output_folder}?"
    #         )
    #         confirm_dialog.setIcon(QMessageBox.Icon.Question)
    #         confirm_dialog.setStandardButtons(
    #             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    #         )
    #         result = confirm_dialog.exec()
    #
    #         if result == QMessageBox.StandardButton.No:
    #             return
    #         else:
    #             if not os.path.exists(output_folder):
    #                 os.makedirs(output_folder)
    #             self.output_folder = output_folder
    #
    #     thread = threading.Thread(target=self.start_downloading)
    #     thread.daemon = True  # Set the thread to daemon mode
    #     thread.start()

    def open_downloaded_folder(self):
        if hasattr(self, 'output_folder'):
            try:
                subprocess.Popen(['xdg-open', self.output_folder])
            except Exception as e:
                print(f"Error opening folder: {e}")
def show_splash(app: QApplication):
    """
    Show a splash screen while the application is loading.
    """
    splash_pix = QPixmap(get_file("pylist/assets/", "splash_small.png"))
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    # Show splash screen
    splash.show()
    app.processEvents()
    # Simulate a time-consuming operation
    time.sleep(2)
    # Close splash and continue with the main application
    splash.close()


def gui():
    """
    Run the GUI application.
    Returns:
        None
    """
    app = PySide6.QtWidgets.QApplication(sys.argv)
    show_splash(app)

    if IS_WINDOWS_EXE:
        theme_path = get_file("pylist/assets/", "dark_teal.xml")
    else:
        theme_path = "dark_teal.xml"

    icon_path = get_file("pylist/assets/", "icon_256.ico")

    apply_stylesheet(app, theme=theme_path)  # Apply the dark teal theme

    app_icon = QIcon(icon_path)  # Create a QIcon object
    app.setWindowIcon(app_icon)  # Set the app icon BEFORE creating the window

    ex = App()
    ex.setWindowIcon(app_icon)  # Usually redundant, but can't hurt.

    sys.exit(app.exec())


if __name__ == "__main__":
    gui()
