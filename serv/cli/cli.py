import os
from time import sleep


def start_cli_interface() -> None:
    # sleep for a bit to let the flask server and other threads start up
    sleep(2)
    while True:
        command = input("sprobbler> ")
        print("silly goose")
