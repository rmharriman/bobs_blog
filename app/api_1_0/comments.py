from flask import request, jsonify, g, url_for, current_app
from . import api
from ..models import Comment, Post, Permission
from .decorators import permission_required
from .. import db


@api.route("/comments/")
def get_comments():
    page = request.args.get("page", 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config["BLOG_COMMENTS_PER_PAGE"],
        error_out=False)
    comments = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for("api.get_comments", page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for("api.get_comments", page=page+1, _external=True)
    return jsonify({
        "comments": [comment.to_json() for comment in comments],
        "prev": prev,
        "next": next,
        "count": pagination.total
    })


@api.route("/comments/<int:id>")
def get_comment(id):
    comment = Comment.query.get_or_404(id)
    return jsonify({"comment": comment.to_json()})
