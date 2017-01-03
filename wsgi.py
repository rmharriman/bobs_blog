import os
from app import create_app

"""
WSGI file used to create instance of the application for Gunicorn
"""

if os.path.exists('.env'):
    print('Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

# create an instance of the application and read in config setting from environment
app = create_app(os.getenv("FLASK_CONFIG") or "default")
