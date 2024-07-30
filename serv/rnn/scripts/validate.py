#!/usr/bin/env python3

import os
import sys
import librosa

file_cnt = 0

def validate_music_file(file_path):
    global file_cnt

    print(f"Checking {file_path}")

    y, sr = librosa.load(file_path)
    file_cnt += 1

    if librosa.get_duration(y=y, sr=sr) != 30:
        print("Invalid!")
        return False

    return True

if __name__ == "__main__":
    directory = sys.argv[1]
    print(f"Checking dir {directory}")
    for (root, dirs, files) in os.walk(directory, followlinks=True, topdown=True):
        for file in files:
            path = os.path.join(root, file)
            if not validate_music_file(path):
                sys.exit(1)



    print(f"Checked {file_cnt} files")
