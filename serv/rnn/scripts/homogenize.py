#!/usr/bin/env python

import os
import sys
import pathlib

with os.scandir(sys.argv[1]) as it:
    for i, entry in enumerate(it):
        original = pathlib.Path(entry.path)
        target = pathlib.Path(sys.argv[1] + "/" + str(i) + original.suffix)
        print(f"{original} -> {target}")
        original.rename(target)
