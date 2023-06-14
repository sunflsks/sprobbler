import os
from config import Config


def debugprint(*args, **kwargs):
    if Config().debug_enabled():
        print("DEBUG: " + " ".join(map(str, args)), **kwargs)
    else:
        with open("/tmp/sprobbler_debug.log") as f:
            print(" ".join(map(str, args)), **kwargs, file=f)
