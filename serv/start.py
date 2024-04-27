#!/usr/bin/env python3

import os
from cli.cli import start_cli_interface
from scrobbler.scrobbler import start_scrobbler
from config import Config
from threading import Thread

print("ONLY FOR DEVELOPMENT USE!!! DANGEROUS ENV VARS SET !!!!")

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "True"
os.environ["SPROBBLER_DEBUG"] = "YES"


def start_flask_server():
    app = create_app()
    app.run(host="0.0.0.0", port=Config().port())


if __name__ == "__main__":
    if not Config().validate_config():
        exit(1)

    from db import init_db_if_not_exists
    from web.app import create_app

    init_db_if_not_exists()

    Thread(target=start_flask_server).start()
    Thread(target=start_scrobbler).start()
    Thread(target=start_cli_interface).start()
