import os
import acoustid
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TIT2, TPE1

file_path = os.path.join(".gitignore", "ACOUSTID_API_KEY")
# Check if the API key file exists; if not, create it with user input
if not os.path.isfile(file_path):
    ACOUSTID_API_KEY = input("Enter your ACOUSTID API key: ")
    with open(file_path, 'w') as f:
        f.write(ACOUSTID_API_KEY)
else:
    with open(file_path, 'r') as f:
        ACOUSTID_API_KEY = f.read()

print(ACOUSTID_API_KEY)
exit()

def identify_track(file_path):
    """
    Generates a fingerprint for the file and queries AcoustID.
    Returns (title, artist, album) if found, else None.
    """
    try:
        duration, fingerprint = acoustid.fingerprint_file(file_path)
        print(f"Duration: {duration}")
        print(f"Fingerprint: {fingerprint[:60]}...")  # print first 60 chars for inspection
    except acoustid.FingerprintGenerationError as e:
        print(f"Error generating fingerprint for {file_path}: {e}")
        return None
    
    try:
        results = acoustid.lookup(ACOUSTID_API_KEY, fingerprint, duration)
    except acoustid.AcoustidError as e:
        print(f"AcoustID lookup error for {file_path}: {e}")
        return None

    # Process the results (we take the first result and its first recording)
    if results.get('results'):
        best_match = results['results'][0]
        if 'recordings' in best_match and best_match['recordings']:
            recording = best_match['recordings'][0]
            title = recording.get('title')
            # Pick the first artist if available
            artist = recording.get('artists', [{}])[0].get('name', '')
            # Attempt to get the album name from the first release (if available)
            album = None
            if 'releases' in recording and recording['releases']:
                album = recording['releases'][0].get('title')
            return title, artist, album
    return None

def update_id3_tags(file_path, title, artist, album):
    """
    Updates the MP3 file's ID3 tags with the given title, artist, and album.
    """
    try:
        # Attempt to load existing ID3 tags or create new ones
        try:
            audio = EasyID3(file_path)
        except Exception:
            audio = EasyID3()
        audio['title'] = title
        if artist:
            audio['artist'] = artist
        if album:
            audio['album'] = album
        audio.save(file_path)
    except Exception as e:
        print(f"Failed to update metadata for {file_path}: {e}")

def safe_filename(name):
    """
    Returns a filename-safe version of the track title.
    Removes or replaces characters that are illegal in filenames.
    """
    # Remove characters that are not allowed in filenames (on most OSes)
    return "".join(c for c in name if c.isalnum() or c in " ._-").strip()

def main():
    # Process all MP3 files in the current folder
    for filename in os.listdir('.'):
        if filename.lower().endswith('.mp3'):
            print(f"\nProcessing: {filename}")
            identification = identify_track(filename)
            if identification:
                title, artist, album = identification
                if not title:
                    print("No title found for this track.")
                    continue
                if album:
                    print(f"Identified as: {title} by {artist} from album: {album}")
                else:
                    print(f"Identified as: {title} by {artist}")
                update_id3_tags(filename, title, artist, album)
                new_name = f"{safe_filename(title)}.mp3"
                # If the new filename already exists, add a counter to avoid overwriting
                counter = 1
                final_name = new_name
                while os.path.exists(final_name):
                    final_name = f"{safe_filename(title)}_{counter}.mp3"
                    counter += 1
                try:
                    os.rename(filename, final_name)
                    print(f"Renamed to: {final_name}")
                except Exception as e:
                    print(f"Error renaming {filename} to {final_name}: {e}")
            else:
                print("Could not identify the track.")

if __name__ == "__main__":
    main()
