from flask import render_template, session, redirect, url_for, current_app
from . import main
from .forms import NameForm
from .. import db
from ..models import User
from ..email import send_email


# Important to remember route decorator comes from the bp not app
@main.route("/", methods=["GET", "POST"])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session["known"] = False
            if current_app.config.get("BLOG_ADMIN"):
                send_email(current_app.config.get("BLOG_ADMIN"), "New User",
                           'mail/new_user', user=user)
        else:
            session["known"] = True
        session["name"] = form.name.data
        # URL for function arg is also different with bp's
        # No longer can routes be accessed with just name of the view function
        # Flask applies a namespace to all endpoints in a bp (namespace is name of bp)
        ## so multiple bp's can be defined
        # index() view func is registered as main.index
        # shorthand is supported tho so .index works - in this case bp for current request is used
        # redirects in same bp can use shorthand, across bp's must use full namespaced endpoint
        return redirect(url_for(".index"))
    return render_template("index.html",
                           form=form, name=session.get("name"),
                           known=session.get("known", False))

@main.route("/user/<username>")
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template("user.html", user=user)
