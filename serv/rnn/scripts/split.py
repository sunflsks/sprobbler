#!/usr/bin/env python3

# Split up given audio file into segments and save them as individual files

import os
import sys
import librosa
import soundfile as sf
from pathlib import Path
from threading import Thread
from multiprocessing import Pool

SECONDS_PER_SEGMENT = 30

def split_audio(input_file, output_dir):
        # Split input file and put it into the output dir specified
        print(f"Decoding {input_file}")
        sys.stdout.flush()

        y, sr = librosa.load(input_file)

        duration = librosa.get_duration(y=y, sr=sr)
        segments = int(duration / SECONDS_PER_SEGMENT)

        # Automatically cut off first segment. If current segment is shorter than 15 seconds, cut
        # it off as well as the previous segment. If last segment is longer than 16 seconds, cut it off
        # and keep the previous segment

        series_to_write = []

        for s in range(1, segments):
                start_sample = SECONDS_PER_SEGMENT * s * sr
                end_sample = SECONDS_PER_SEGMENT * (s+1) * sr

                if end_sample > len(y):
                        if len(y[start_sample:]) < (SECONDS_PER_SEGMENT / 2) * sr:
                                series_to_write.pop()
                        break
        
                series_to_write.append(y[start_sample:end_sample])
        
        stem = Path(input_file).stem

        for i, series in enumerate(series_to_write):
            segment_path = output_dir + "/" + stem + "-" + str(i) + ".wav"
            print(f"Writing file {segment_path}")
            sys.stdout.flush()
            sf.write(segment_path, series, sr)
                
                
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Incorrect usage")
        sys.exit(1)

    original_dir = sys.argv[1]
    new_dir = sys.argv[2]

    try:
        os.mkdir(new_dir)
    except FileExistsError:
        print("New directory must not exist!")
        sys.exit(1)

    with Pool() as pool:
        pool.starmap(split_audio, [(os.fsdecode(file), new_dir) for file in os.scandir(original_dir)])

