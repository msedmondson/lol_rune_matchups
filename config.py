"""
This file should contain absolute paths for the app to include them
as modules
"""
import os
basedir = os.path.abspath(os.path.dirname('app/db/'))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False
