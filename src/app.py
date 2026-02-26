from serato_tools import database_v2
from pathlib import Path
import os
import shutil
from collections import defaultdict
db = database_v2.DatabaseV2()


def fix_tracks(db: database_v2.DatabaseV2):
    tracks = db.get_track_paths()

    for track in tracks:
        index = tracks.index(track)
        tracks[index] = f"/{track}"

    return tracks


def compare_files(tracks: list[str], parent_files: list[Path]):
    missing_files = []
    for file in parent_files:

        try:
            index = tracks.index(str(file))

            if index > -1:
                print(f"Found {file} in tracks")
            else:
                print(f"Did not find {file} in tracks")
        except ValueError:
            missing_files.append(file)
    return missing_files

def get_file_tracks(files:list[Path]):
    result=[]
    for file in files:
        result.append(str(file))
    return result

tracks=fix_tracks(db) 


file = Path(db.DEFAULT_DATABASE_FILE)


parent = file.parent.parent


parent_files = get_file_tracks(list(parent.glob("**/*.*")))

def filter_music_files(files:list[Path]):
    result = []
    for file in files:
        if Path(file).suffix.lower() in [".mp3", ".wav", ".flac", ".aac", ".ogg",".mp4",".flac",".aif",".wav"]:
            result.append(file)
    return result

parent_files = filter_music_files(parent_files)
e= [a.suffix for a in parent.glob("**/*.*")]
grouped = defaultdict(list)


for a in e:
    grouped[a].append(a)
    
for g in grouped:
    print(g)
missing_files = compare_files(tracks, parent_files)
# Find Tracks in Music Directory



# Create a new folder for missing files
if not os.path.exists(parent / "missing_files"):
    os.mkdir(parent / "missing_files")

missing_folder = Path(parent / "missing_files")
directory_errors=0
# Copy Missing files to the new folder
for file in missing_files:
    try:

        shutil.move(file, missing_folder)
       
        print(f"Copied {file} to {missing_folder}")
    except IsADirectoryError:
        directory_errors+=1
    except Exception as e:
        os.remove(file)
        print(f"Error copying {file} to {missing_folder}: {e}")

print(db)
