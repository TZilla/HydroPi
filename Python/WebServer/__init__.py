from flask import Flask

from flask_bootstrap import Bootstrap
import os
from flask.ext.pymongo import PyMongo

app = Flask(__name__) 
mongo=PyMongo(app)
app.secret_key = os.urandom(24)    
Bootstrap(app)

import WebServer.routes