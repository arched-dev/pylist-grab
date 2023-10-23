import os
import sys
import threading
import time

from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QPixmap, QAction, QIcon
from PyQt6.QtWidgets import (
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
    QDialog,
    QStackedWidget,
    QGraphicsScene,
    QGraphicsView,
    QMainWindow,
)
from qt_material import apply_stylesheet

from pylist.downloader import (
    download_playlist,
    validate_playlist,
)  # Replace these imports with your actual functions


class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()


class ImageDialog(QDialog):
    def __init__(self, image_path):
        super().__init__()
        self.setWindowTitle("Example Image")
        layout = QVBoxLayout()
        graphics_view = QGraphicsView()
        scene = QGraphicsScene()
        pixmap = QPixmap(image_path)
        scene.addPixmap(pixmap)
        graphics_view.setScene(scene)
        layout.addWidget(graphics_view)
        self.setLayout(layout)


class HowToBase(QDialog):
    def __init__(self, pages: list, title: str):
        super().__init__()
        self.setWindowTitle(title)
        self.setModal(True)

        self.stacked_widget = QStackedWidget()

        for page in pages:
            self.stacked_widget.addWidget(
                self.create_page(page["text"], page["image_path"])
            )

        self.current_page_index = 0

        # Create Next and Back buttons
        button_layout = QHBoxLayout()
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.go_next)
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setEnabled(False)
        button_layout.addWidget(self.back_button)
        button_layout.addWidget(self.next_button)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.show()

    def create_page(self, text, image_path):
        page = QWidget()
        layout = QVBoxLayout()

        text_label = QLabel()
        text_label.setText(text)
        layout.addWidget(text_label)

        thumbnail = QPixmap(image_path).scaled(
            200, 200, Qt.AspectRatioMode.KeepAspectRatioByExpanding
        )
        thumbnail_label = QLabel()
        thumbnail_label.setPixmap(thumbnail)

        layout.addWidget(thumbnail_label)
        page.setLayout(layout)

        return page

    def go_next(self):
        if self.current_page_index < self.stacked_widget.count() - 1:
            self.stacked_widget.setCurrentIndex(self.current_page_index + 1)
            self.back_button.setEnabled(True)
            self.current_page_index += 1
        if self.current_page_index == self.stacked_widget.count() - 1:
            self.next_button.setEnabled(False)

    def go_back(self):
        if self.current_page_index > 0:
            self.stacked_widget.setCurrentIndex(self.current_page_index - 1)
            self.next_button.setEnabled(True)
            self.current_page_index -= 1
        if self.current_page_index == 0:
            self.back_button.setEnabled(False)


class HowToWindow(HowToBase):
    def __init__(self):
        title = "How to Get a Valid YouTube Playlist URL"
        pages = [
            {
                "text": "First, head over to YouTube and use the search bar to look for a genre or artist. Avoid searching for specific songs at this stage.",
                "image_path": "./assets/page_1.png",
            },
            {
                "text": "Once the search results are displayed, locate the 'Filter' button at the upper-right corner of the page. \n\nClick it and select 'Playlist' from the dropdown options.",
                "image_path": "./assets/page_2.png",
            },
            {
                "text": "Browse through the filtered results to find a playlist that catches your interest. Ensure that the thumbnail indicates multiple videos, or look for a listing that includes a 'VIEW FULL PLAYLIST' button. \n\nOpen the playlist you've chosen.",
                "image_path": "./assets/page_3.png",
            },
            {
                "text": "After the playlist page has loaded, you'll see the playlist title at the top, right above a list of videos. Click on the playlist title to proceed.",
                "image_path": "./assets/page_4.png",
            },
            {
                "text": "You should now be on the playlist's dedicated page. Verify this by checking if the URL starts with 'youtube.com/playlist?...'. \n\nIf it does, go ahead and copy the URL, then paste it into this application.",
                "image_path": "./assets/page_5.png",
            },
        ]
        super().__init__(pages, title)


class App(QMainWindow):
    download_progress = pyqtSignal(int, str, str, str, str)

    def __init__(self):
        super(App, self).__init__()
        self.playlist_length = 0
        self.initUI()

    def initUI(self):
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

        self.folder_button = QPushButton("Select Output Folder")
        self.folder_button.setEnabled(False)
        self.folder_button.clicked.connect(self.select_folder)
        layout.addWidget(self.folder_button)

        self.genre_input = QLineEdit("Enter Genre")
        self.genre_input.setEnabled(False)
        layout.addWidget(self.genre_input)

        self.download_button = QPushButton("Start Downloading")
        self.download_button.setEnabled(False)
        self.download_button.clicked.connect(self.confirm_and_start_downloading)
        layout.addWidget(self.download_button)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setMinimumHeight(200)
        self.scroll_content = QWidget(self.scroll)
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        layout.addWidget(self.scroll)

        self.progress_label = QLabel("0/0")
        layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Set the layout to the central widget
        central_widget.setLayout(layout)

        self.setWindowTitle("MP3 Downloader")
        self.setMinimumWidth(500)

        self.download_progress.connect(self.update_progress)
        self.show()

    def restore_placeholder(self):
        if not self.url_input.hasFocus() and not self.url_input.text():
            self.url_input.setPlaceholderText("Enter Playlist URL")

    def focusInEvent(self, event):
        self.url_input.setPlaceholderText("")

    def create_menu(self):
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
        find_url_action.triggered.connect(self.open_how_to_window)

        # Create actions for About menu
        about_action = QAction("About", self)
        about_action.triggered.connect(self.open_about_dialog)

        # Add actions to menus
        file_menu.addAction(close_action)
        view_menu.addAction(what_it_does_action)
        view_menu.addAction(find_url_action)
        about_menu.addAction(about_action)

    def close_app(self):
        self.close()

    def open_how_to_window(self):
        self.how_to_window = HowToWindow()
        self.how_to_window.show()

    def open_what_it_does(self):
        msg = QMessageBox()
        msg.setWindowTitle("What it does")
        msg.setText(
            "This application enables you to download entire YouTube playlists in MP3 format while also populating the files with as much metadata as possible, including album artwork. \n\n"
            "While streaming services have largely rendered MP3s obsolete for the average listener, they remain essential for DJs and other professionals who need direct access to audio files.\n\nWell-formatted metadata makes it easier to manage your song catalog effectively.\n\nPlease note that this project serves as a proof of concept to demonstrate the technical feasibility of such a service. We do not endorse or encourage the unauthorized distribution of copyrighted material. Always remember to support your favorite artists by purchasing their music legally."
        )
        msg.exec()

    def open_about_dialog(self):
        msg = QMessageBox()
        msg.setWindowTitle("About")
        msg.setText(
            "GUI and cli interface & metadata injection written by Lewis Morris (lewis.morris@gmail.com)\n\n Libraries Used and Loved: \n pytube \n moviepy \n mutagen \n PyQt6 \n qt_material"
        )
        msg.exec()

    def validate_url(self):
        url = self.url_input.text()
        try:
            self.playlist = validate_playlist(url)
            if self.playlist:
                self.folder_button.setEnabled(True)
                self.download_button.setEnabled(True)
                self.genre_input.setEnabled(True)
                self.playlist_length = len(self.playlist.video_urls)
        except Exception:
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
                self.show_how_to_window()

    def show_how_to_window(self):
        self.how_to_window = HowToWindow()

    def select_folder(self):
        self.output_folder = QFileDialog.getExistingDirectory(
            self, "Select Output Folder"
        )

    def disable_all(self):
        self.download_button.setEnabled(False)
        self.genre_input.setEnabled(False)
        self.folder_button.setEnabled(False)
        self.validate_url_button.setEnabled(False)
        self.url_input.setEnabled(False)

    def confirm_and_start_downloading(self):
        if not hasattr(self, "output_folder"):
            desktop = os.path.join(os.path.join(os.path.expanduser("~")), "Desktop")
            self.output_folder = os.path.join(desktop, "YouTube MP3s")
            if not os.path.exists(self.output_folder):
                os.makedirs(self.output_folder)

            confirm_dialog = QMessageBox(self)
            confirm_dialog.setWindowTitle("Confirm Folder")
            confirm_dialog.setText(
                f"You have not selected an output directory. Are you happy to save files to {self.output_folder}?"
            )
            confirm_dialog.setIcon(QMessageBox.Icon.Question)
            confirm_dialog.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            result = confirm_dialog.exec()

            if result == QMessageBox.StandardButton.No:
                return

        threading.Thread(target=self.start_downloading).start()

    @pyqtSlot(int, str, str, str, str)
    def update_progress(self, i, artist, title, duration, estimated_remaining):
        percent = int((i / self.playlist_length) * 100)
        self.progress_bar.setValue(percent)

        song_label = QLabel(f"Downloaded: {artist} - {title} (Took: {duration} mm:ss)")
        sub_layout = QVBoxLayout()
        sub_layout.addWidget(song_label)

        self.scroll_layout.insertLayout(0, sub_layout)
        self.progress_label.setText(
            f"{i}/{self.playlist_length} (Estimated time remaining: {estimated_remaining} mm:ss)"
        )

    total_time = 0  # Total time taken for all songs in seconds

    def start_downloading(self):
        self.download_button.setText("Downloading...")
        self.disable_all()

        self.total_time = 0  # Initialize total_time

        for i, (song_meta, time_taken) in enumerate(
            download_playlist(self.playlist, self.output_folder)
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

            self.download_progress.emit(
                i + 1, artist, title, duration, estimated_remaining_str
            )
            time.sleep(0.1)

        self.download_button.setText("Start Downloading")


def gui():
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme="dark_teal.xml")  # Apply the dark teal theme
    ex = App()
    ex.setWindowIcon(QIcon("./assets/icon_256.ico"))
    sys.exit(app.exec())


if __name__ == "__main__":
    gui()
