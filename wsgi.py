import os
from app import create_app

"""
WSGI file used to create instance of the application for Gunicorn
"""

# create an instance of the application and read in config setting from environment
app = create_app(os.getenv("FLASK_CONFIG") or "default")
