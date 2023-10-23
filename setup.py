from setuptools import setup, find_packages

# Read the content of README.md
with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()


setup(
    name="pylist",
    version="0.0.1",
    packages=find_packages(),
    url="https://github.com/lewis-morris/pylist",
    license="MIT",
    author="lewis",
    author_email="lewis.morris@gmail.com",
    description="YouTube playlist grabber with metadata",
    long_description=readme,  # This is the new line
    long_description_content_type="text/markdown",  # This is the new line
    entry_points={
        "console_scripts": [
            "pylist=pylist.cli:main",
            "pylist-gui=pylist.gui:gui",
        ]
    },
    package_data={
        "pylist": ["pylist/assets/*.png", "pylist/assets/*.ico"],
    },
    install_requires=[
        "requests~=2.31.0",
        "pytube~=15.0.0",
        "moviepy~=1.0.3",
        "mutagen~=1.47.0",
        "pyqt6~=6.4.2",
        "setuptools~=68.0.0",
        "qt_material~=2.4.0",
    ],
)
