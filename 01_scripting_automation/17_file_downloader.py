"""
Script: File Downloader
What it does: Downloads a file from the internet and saves it locally.
Shows download progress as a percentage.

Install: pip install requests
"""

import os

try:
    import requests  # popular library for making HTTP requests

    def download_file(url, save_path):
        """Download a file from a URL and save it to disk."""
        print(f"Downloading: {url}")

        # stream=True means download in chunks (good for large files)
        response = requests.get(url, stream=True)

        # Check if the request was successful (200 = OK)
        if response.status_code != 200:
            print(f"Failed to download. Status code: {response.status_code}")
            return False

        # Get total file size from headers (may not always be available)
        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0
        chunk_size = 8192  # download 8KB at a time

        with open(save_path, "wb") as f:  # "wb" = write in binary mode
            for chunk in response.iter_content(chunk_size=chunk_size):
                f.write(chunk)             # write each chunk to file
                downloaded += len(chunk)

                # Show progress
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\r  Progress: {percent:.1f}% ({downloaded} bytes)", end="")

        print(f"\n✓ Saved to: {save_path}")
        return True

    # Download a small public file (Python logo PNG)
    url = "https://www.python.org/static/img/python-logo.png"
    download_file(url, "python_logo.png")

    # Show file size
    if os.path.exists("python_logo.png"):
        size = os.path.getsize("python_logo.png")
        print(f"  File size: {size} bytes")
        os.remove("python_logo.png")

except ImportError:
    print("requests not installed. Run: pip install requests")
