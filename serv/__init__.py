import os
from flask import Flask

from web.flask_init import instantiate_web_server

server = instantiate_web_server()
server.run()
