#!/usr/bin/env python3

# Consolidate all the music files in a folder into a single nd numpy array with a dimension for sample # and mfcc count, and save said array to disk for later usage.

import os
import sys
import librosa
import numpy as np
import math
import librosa
from alive_progress import alive_bar

# We know that all music files are 30 seconds in length, so we can hardcode this

MUSIC_FILE_LENGTH = 30 # seconds
SEGMENTS_PER_FILE = 6
SECONDS_PER_SEGMENT = MUSIC_FILE_LENGTH / SEGMENTS_PER_FILE # 5 seconds
HOP_LENGTH = 512 # sensible default
MFCC_COUNT = 13 # Good number AFAIK (https://dsp.stackexchange.com/questions/28898/mfcc-significance-of-number-of-features)

if __name__ == "__main__":
    dirpath = sys.argv[1]
    mfcc_list = []
    mfcc_count = 0

    number_of_files = len(os.listdir(dirpath))

    print(f"Processing MFCCs for {dirpath}")

    with alive_bar(number_of_files * SEGMENTS_PER_FILE) as bar:
        for file in os.scandir(dirpath):
            y, sr = librosa.load(os.fsdecode(file.path))

            for s in range(0, SEGMENTS_PER_FILE):
                start = int(s * sr * SECONDS_PER_SEGMENT)
                end = int((s+1) * sr * SECONDS_PER_SEGMENT)

                mfcc = librosa.feature.mfcc(y=y[start:end], sr=sr, hop_length=HOP_LENGTH, n_mfcc=MFCC_COUNT).T
                # make sure length is good; if so, then add to global mfcc list

                if len(mfcc) == math.ceil((end - start) / HOP_LENGTH):
                    mfcc_list.append(mfcc)
                    bar()

    # Convert to numpy array and save to disk
    save_path = os.path.join(dirpath, "mfccs")
    print(f"Saving array to {save_path}")
    print(f"New shape: {(len(mfcc_list), *mfcc_list[0].shape)}")

    np.save(save_path, np.asarray(mfcc_list))
