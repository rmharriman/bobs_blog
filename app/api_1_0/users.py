from flask import jsonify, request, g, abort, url_for, current_app
from .. import db
from .decorators import permission_required
from .errors import forbidden
from . import api
from ..models import User


@api.route("/users/<int:id>")
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())
