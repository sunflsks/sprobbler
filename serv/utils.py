import os
from textwrap import wrap
from config import Config
from threading import Timer


def debugprint(*args, **kwargs):
    if Config().debug_enabled():
        print("DEBUG: " + " ".join(map(str, args)), **kwargs)
    else:
        with open("/tmp/sprobbler_debug.log") as f:
            print(" ".join(map(str, args)), **kwargs, file=f)


def repeat(seconds):
    def decorator(func):
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            Timer(seconds, wrapper, args=list(args), kwargs=kwargs).start()

        return wrapper

    return decorator
