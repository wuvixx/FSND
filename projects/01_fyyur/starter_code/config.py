import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
# SQLALCHEMY_DATABASE_URI = '<Put your local database url>'
SQLALCHEMY_DATABASE_URI = 'postgres://postgres:123@127.0.0.1:5432/fyyur'
SQLALCHEMY_TRACK_MODIFICATIONS = False