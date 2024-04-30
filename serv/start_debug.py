#!/usr/bin/env python3

import os
from scrobbler.scrobbler import start_scrobbler
from config import Config
from threading import Thread

print("ONLY FOR DEVELOPMENT USE!!! DANGEROUS ENV VARS SET !!!!")

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "True"
os.environ["SPROBBLER_DEBUG"] = "YES"


def start_flask_server():
    app = create_app()
    app.run(host="0.0.0.0", port=int(Config.get(Config.Keys.PORT)))


if __name__ == "__main__":
    if not Config.validate():
        exit(1)

    from web.app import create_app

    Thread(target=start_flask_server).start()
    Thread(target=start_scrobbler).start()
