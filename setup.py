from setuptools import setup

setup(
    name="pylist",
    version="0.0.1",
    packages=["pylist"],
    url="pylist",
    license="mit",
    author="lewis",
    author_email="lewis.morris@gmail.com",
    description="youtube playlist grabber with metadata",
    entry_points={
        "console_scripts": [
            "pylist = pylist.cli:main",  # For the command-line tool
            "pylist-gui = pylist.gui:gui",  # For the GUI
        ],
    },
    package_data={
        "pylist": ["assets/*.jpg"],  # Include all .jpg files in the assets folder
    },
    install_requires=[
        "requests~=2.31.0",
        "pytube~=15.0.0",
        "moviepy~=1.0.3",
        "mutagen~=1.47.0",
        "pyqt6~=6.4.2",
        "setuptools~=68.0.0",
        "qt_material~=2.4.0",  # Assuming you meant 'qt_material' instead of 'qt_materail'
    ],
)
