import os
import subprocess
import mimetypes
import requests
import shutil  # for moving files
from mutagen import File
from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3, ID3NoHeaderError
from ytmusicapi import YTMusic
from ytmusicapi.setup import setup

# You might have to go delete archive.txt from the downloads
# subfolder to successfully add music!

# use 'LM' for your private liked music playlist! (requires auth header)
# Can also use other playlists!
YT_PLAYLIST = 'LM'

# Set up ffmpeg path so yt-dlp works [MAY BE DIFFERENT!] Windows Binary included.
os.environ["PATH"] = os.path.join(os.getcwd(), "ffmpeg\bin;") + os.environ["PATH"]

# Setup headers [WILL BE DIFFERENT!!] 
setup(
    filepath=os.path.join(".gitignore","headers_auth.json"),
    headers_raw="""<Paste_raw_headers_from_first_ytmusic_POST_request_headers>"""
)
print("[INFO] Headers saved to {os.path.join('.gitignore','headers_auth.json')}")

# Paths
downloads_folder = os.path.join(os.getcwd(), "downloads")
archive_path = os.path.join(downloads_folder, "archive.txt")

# Use %APPDATA% to build the path to yt-dlp.exe [MAY BE DIFFERENT!]
yt_dlp_exe = os.path.join(os.environ["APPDATA"], "Python", "Python313", "Scripts", "yt-dlp.exe")
sort_folder = os.path.join(os.getcwd(), "sort")

def main():
    os.makedirs(downloads_folder, exist_ok=True)
    # 1) Unscrew: Move any previously sorted MP3s from 'sort/' back to 'downloads/'
    # unsort_mp3s_from_artist_album()

    # 2) Download new Liked Songs
    ytmusic = YTMusic(os.path.join(".gitignore","headers_auth.json"))
    if YT_PLAYLIST == 'LM':
        playlist = ytmusic.get_liked_songs(limit=1500)
    else:
        playlist = ytmusic.get_playlist(YT_PLAYLIST, limit=1500)
    tracks = playlist.get("tracks", [])

    # YT-DLP format
    output_template = "%(title)s [%(album)s].%(ext)s"

    # Build list of video URLs
    urls = [f"https://www.youtube.com/watch?v={t['videoId']}" for t in tracks if "videoId" in t]

    # Write URLs to a temporary batch file
    urls_file = os.path.join(downloads_folder, "urls.txt")
    with open(urls_file, "w", encoding="utf-8") as f:
        for url in urls:
             f.write(url + "\n")

    print(f"[INFO] Downloading {len(urls)} songs...")
    subprocess.run([
        yt_dlp_exe,
        "-x", "--audio-format", "mp3",
        "--add-metadata",
        "--embed-thumbnail",
        "--download-archive", archive_path,
        "-o", os.path.join(downloads_folder, output_template),
        "--no-playlist", "--no-call-home",
        "--batch-file", urls_file
    ])

    # 3) Move them back into Artist\Album subfolders
    move_mp3s_into_artist_album()

def unsort_mp3s_from_artist_album():
    """
    Recursively walk 'sort_folder' and move all .mp3 files back into 'downloads_folder'.
    """
    if not os.path.isdir(sort_folder):
        print(f"[UNSORT] Sort folder not found: {sort_folder}")
        return

    print(f"[UNSORT] Moving all mp3s from '{sort_folder}' back to '{downloads_folder}'...")
    for root, dirs, files in os.walk(sort_folder):
        for filename in files:
            if filename.lower().endswith(".mp3"):
                source_path = os.path.join(root, filename)
                dest_path = os.path.join(downloads_folder, filename)
                try:
                    shutil.move(source_path, dest_path)
                except Exception as e:
                    print(f"[WARN] Could not move {source_path} -> {dest_path}: {e}")
    print("[UNSORT] Done.")

def move_mp3s_into_artist_album():
    """
    Re-sorts each .mp3 in 'downloads_folder' into 'sort_folder' subfolders: Artist\Album
    Only uses the first artist in the ID3 tag if multiple.
    """
    print("[SORT] Sorting music")
    os.makedirs(sort_folder, exist_ok=True)

    for filename in os.listdir(downloads_folder):
        if not filename.lower().endswith(".mp3"):
            continue  # skip non-mp3

        source_path = os.path.join(downloads_folder, filename)
        try:
            audio = EasyID3(source_path)
        except Exception:
            audio = File(source_path, easy=True)

        if not audio:
            print(f"[WARN] Can't read tags from: {filename}")
            main_artist = "UnknownArtist"
            album = "UnknownAlbum"
        else:
            # get artist, keep only first if multiple
            all_artists = audio.get("artist", ["UnknownArtist"])[0]
            first_artist = all_artists.split(",", 1)[0].strip()

            album_str = audio.get("album", ["UnknownAlbum"])[0]

            main_artist = safe_folder_name(first_artist)
            album = safe_folder_name(album_str)

        dest_folder = os.path.join(sort_folder, main_artist, album)
        os.makedirs(dest_folder, exist_ok=True)

        dest_path = os.path.join(dest_folder, filename)
        # print(f"[SORT] Moving {filename} -> {dest_path}")
        shutil.move(source_path, dest_path)
    print(f"[SORT] done moving to {sort_folder}")

def safe_folder_name(name):
    # remove or replace chars not allowed in Windows folder names, etc.
    forbidden = r'<>:"/\|?*'
    return "".join(c for c in name if c not in forbidden).strip()

if __name__ == "__main__":
    main()
