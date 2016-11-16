from flask import Blueprint
# Blueprints define routes but are dormant until registered w/app

# First instantiate an object of class Blueprint
# args are blueprint name and module/package where it's located
# 2nd arg is usually name
main = Blueprint("main", __name__)


# importing routes and error pages associates them with bp
## must import them after the bp instance is created to avoid circular import
from . import views, errors
from ..models import Permission


# Context processors can be used to make variables available globally to all templates
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
