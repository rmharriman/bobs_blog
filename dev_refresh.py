#!/usr/bin/env python
# script is made an executable and env utility is used so the venv python is executed
import os
from app import create_app, db
from app.models import User, Role, Post, Permission, Follow
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

# create an instance of the application and read in config setting from environment
app = create_app(os.getenv("FLASK_CONFIG") or "default")
manager = Manager(app)
migrate = Migrate(app, db)

app.app_context().push()

print("Loading dev db roles")
Role.insert_roles()

print("Loading dev db users")
User.generate_fake()

print("Loading dev db posts")
Post.generate_fake()


def create_admin_account():
    user = User(email="rmharriman@gmail.com", password="cat", confirmed=True, username="Rob")
    db.session.add(user)
    db.session.commit()
print("Creating admin account")
create_admin_account()
