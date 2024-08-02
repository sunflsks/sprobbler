import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from tensorflow import keras
import numpy as np
import librosa
import json

N_MFCC = 13
SAMPLE_LEN = 5  # seconds
MODEL_PATH = "/home/sudhip/sprobbler/src/serv/rnn/model.keras"
MAPPING_PATH = "/home/sudhip/sprobbler/src/serv/rnn/mapping.json"


# Given a x second MP3 file, load it and split the time series into lower(x/5) 5 second pieces.
def split_song_into_pieces(song_path):
    y, sr = librosa.load(song_path)
    song_duration = librosa.get_duration(y=y, sr=sr)
    cut_song_duration = int(song_duration / SAMPLE_LEN) * SAMPLE_LEN

    end_idx = cut_song_duration * sr
    y = y[:end_idx]

    newshape = (int(cut_song_duration / SAMPLE_LEN), SAMPLE_LEN * sr)
    print(newshape)
    print(end_idx)
    return np.reshape(y, newshape), sr


def get_idxs_from_prediction(prediction, mapping, sample_cnt):
    prediction = prediction.flatten() / sample_cnt
    idxs = np.argsort(prediction)[::-1].flatten()
    print(idxs)

    # Very certain.
    if np.max(prediction) > 0.65:
        return (np.argmax(prediction),)

    # Certain-ish, return top 2 valuesst
    if np.max(prediction) > 0.45:
        return tuple(idxs[0:2])

    # Not very certain on one exactly, but somewhat of an idea of two.
    if np.max(prediction) < 0.40 and prediction[idxs[1]] > 0.20:
        return tuple(idxs[0:2])

    return None


def load_model_and_mapping(model_path=MODEL_PATH, mapping_path=MAPPING_PATH):
    print("Loading model...")

    model = keras.models.load_model(model_path)
    with open(mapping_path, "r") as file:
        mapping = json.load(file)

    return model, mapping


def predict_genres_for_song(song_path, model, mapping):
    arr, sr = split_song_into_pieces(song_path)
    all_mfccs = librosa.feature.mfcc(y=arr, sr=sr, n_mfcc=N_MFCC)
    all_mfccs = np.swapaxes(all_mfccs, 1, 2)

    pred = np.zeros(shape=(len(mapping)))

    sample_cnt = 0
    for mfccs in all_mfccs:
        sample_cnt += 1
        mfccs = mfccs[np.newaxis, ...]
        pred += model.predict(mfccs, verbose=0).flatten()
        print(f"Segment {sample_cnt}")

    idxs = get_idxs_from_prediction(pred, mapping, sample_cnt)
    genres = (
        list(map(lambda x: mapping[str(x)], idxs)) if idxs is not None else "Unknown"
    )

    print(f"Predicted genre for {song_path}: {genres}")
    return genres
