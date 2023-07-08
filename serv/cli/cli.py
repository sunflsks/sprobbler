import os
from time import sleep


def start_cli_interface() -> None:
    # sleep for a bit to let the flask server and other threads start up
    sleep(2)
    while True:
        command = input("sprobbler> ")
        if command == "quit":
            pass
            # aun tengo que implementar un shutdown hook para que se detenga todo
        print(command, flush=True)
