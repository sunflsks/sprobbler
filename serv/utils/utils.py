import os
from textwrap import wrap
from config import Config
from threading import Timer


def debugprint(*args, **kwargs):
    if Config().debug_enabled():
        print("DEBUG: " + " ".join(map(str, args)), **kwargs)
    else:
        with open("/tmp/sprobbler_debug.log", "w+") as f:
            print(" ".join(map(str, args)), **kwargs, file=f)
