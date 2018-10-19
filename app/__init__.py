from flask import current_app, Flask, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import config

app = Flask(__name__)
app.config.from_object(config)

db = SQLAlchemy(app)
from app import views
from app import models
from app.views import *
