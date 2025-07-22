# Ultimate Video Downloader

<img src="https://raw.githubusercontent.com/Lexiiz3417/ultimate-video-downloader/main/image.png" alt="App Screenshot" width="460"/>

A simple and modern desktop application for downloading videos and audio from hundreds of websites. Built with Python, CustomTkinter, and powered by `yt-dlp`.

## ✨ Key Features

* **Modern & User-Friendly GUI**: A clean and easy-to-use interface for everyone.
* **Multi-Site Support**: Download from YouTube, Facebook, TikTok, Instagram, Twitter, and hundreds of other sites.
* **Format Selection**: Download as **Video (MP4)** or **Audio (MP3)**.
* **Quality Options**: Choose video quality (Best, 1080p, 720p, 480p) or audio quality (Best, Good, Standard).
* **Automatic Organization**: Downloads are automatically organized into folders by site and format (e.g., `<chosen_folder>/facebook/videos/`).
* **Multi-Language**: Available in both English and Indonesian.
* **Auto-Dependency Management**: The app automatically downloads `FFmpeg` and `yt-dlp.exe` if they are missing.
* **Built-in Engine Updater**: Update the `yt-dlp` engine to the latest version directly from the app to ensure compatibility.

## 🚀 Installation

1.  Go to the **[Releases](https://github.com/Lexiiz3417/ultimate-video-downloader/releases)** page.
2.  Download the latest `.exe` file from the "Assets" section.
3.  Save `downloader.exe` anywhere and run it. No installation is required.

## 📦 How to Use

1.  Run `downloader.exe`.
2.  Copy the link of the video or audio you want to download.
3.  Paste the link into the input box.
4.  Select the desired format (Video/Audio) and quality.
5.  Click the "Download Now" button.
6.  Choose a folder to save the download.
7.  Wait for the process to finish!

## 🛠️ Built With

* **Python**: The primary programming language.
* **CustomTkinter**: A library for building modern GUI applications.
* **yt-dlp**: The core engine that handles downloading from various sites.
* **Pillow**: A library for image processing.
* **PyInstaller**: To package the application into a single `.exe` file.

---

## Supported Sites

This application uses `yt-dlp` as its download engine, which supports hundreds of websites. For a complete and up-to-date list, please visit their official page:

➡️ **[View the list of sites supported by yt-dlp here](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)**