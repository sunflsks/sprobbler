#!/usr/bin/env python3

import os
import sys
import pathlib
import numpy as np
from tensorflow import keras
from ..make_celery import celery
from tensorflow.keras.layers import *
from sklearn.model_selection import train_test_split


def consolidate_genre_arrays(array_genre_dict):
    # Map each genre to a number (based on its position in the dict), and create a numpy array of dimension (a[:-1], 1)
    x = None
    y = None

    mapping = {}

    for genre_idx, (genre, array) in enumerate(array_genre_dict.items()):
        if x is None:
            x = array_genre_dict[genre]
            y_shape = (*x.shape[:-2], 1)
            y = np.full(y_shape, genre_idx, dtype=int)

        else:
            array = array_genre_dict[genre]
            y_shape = (*array.shape[:-2], 1)

            x = np.concatenate((x, array))
            y = np.concatenate((y, np.full(y_shape, genre_idx, dtype=int)))

        mapping[genre_idx] = genre

    return x, y, mapping


def model_blueprint(shape, num_of_genres):
    return keras.Sequential(
        [
            Input(shape),
            Bidirectional(
                LSTM(
                    512,
                    return_sequences=True,
                    kernel_regularizer=keras.regularizers.l2(0.01),
                )
            ),
            Bidirectional(
                LSTM(
                    256,
                    return_sequences=True,
                    kernel_regularizer=keras.regularizers.l2(0.01),
                )
            ),
            Bidirectional(
                LSTM(
                    256,
                    return_sequences=False,
                    kernel_regularizer=keras.regularizers.l2(0.01),
                )
            ),
            Dense(256, activation="relu"),
            Dropout(0.3),
            Dense(num_of_genres, activation="softmax"),
        ]
    )


def make_sets(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    return X_train, X_test, y_train, y_test


if __name__ == "__main__":
    array_genre_dict = {}

    for sample_dir in os.scandir(sys.argv[1]):
        if sample_dir.is_dir():
            # This directory format is hardcoded as it's what I'm using; feel free to change
            # it around if necessary

            genre = pathlib.PurePath(sample_dir).name
            print(f"Found genre {genre}, loading dict")

            array_path = os.path.join(sample_dir, "mfccs.npy")
            array_genre_dict[genre] = np.load(array_path)

    X, y, mapping = consolidate_genre_arrays(array_genre_dict)
    X_train, X_test, y_train, y_test = make_sets(X, y)
    X_test, X_validate, y_test, y_validate = make_sets(X_test, y_test)

    optimizer = keras.optimizers.Adam(learning_rate=0.0001)

    model = model_blueprint(X.shape[1:], len(array_genre_dict))

    model.compile(
        optimizer=optimizer,
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    model.fit(
        x=X_train,
        y=y_train,
        epochs=25,
        validation_data=(X_test, y_test),
        batch_size=128,
        callbacks=[keras.callbacks.EarlyStopping(patience=3, verbose=1)],
    )

    model.evaluate(x=X_validate, y=y_validate)

    model.save("model.keras")

    with open("mapping.json", "w") as output:
        json.write(output, mapping)
