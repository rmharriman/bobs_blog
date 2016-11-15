from flask import render_template
from . import main


# app_errorhandler is used to handle errors throughout the entire app
# as opposed to errorhandler which only handles errors in the bp
@main.app_errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500
