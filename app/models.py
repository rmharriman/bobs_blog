from datetime import datetime
import hashlib
from flask import current_app, request
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from app import db
from . import login_manager


# SQLAlchemy provides a baseclass with a set of helper functions to inherit
class Role(db.Model):
    # Tablename is optional but convention uses plurals as table names so good practice to have
    __tablename__ = "roles"
    # Remaining class vars are attributes of the model defined as instances of Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    # Relationships add connections between rows in different tables
    # Backref adds role attribute to the user object
    users = db.relationship("User", backref="role")
    
    @staticmethod
    def insert_roles():
        roles = {
            "User": (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES,
                     True),
            "Moderator": (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES, 
                      Permission.MODERATE_COMMENTS, False),
            "Administrator": (0xff, False)            
            }
        
        for r in roles:
            # Tries to find existing roles by name
            role = Role.query.filter_by(name=r).first()
            if role is None:
                # Creates a new role if necessary, else, updates existing role
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()
        
        
    def __repr__(self):
        return "<Role %r>" % self.name


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    confirmed = db.Column(db.Boolean, default=False)
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship("Post", backref="author", lazy="dynamic")
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config["BLOG_ADMIN"]:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
                
        if self.email is not None and self.avatar_hash is None:
            # Good idea to cache the hash as it is a CPU intensive operation
            self.avatar_hash = hashlib.md5(self.email.encode("utf-8")).hexdigest()
    
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({"confirm": self.id})
    
    def confirm(self, token):
        s = Serializer(current_app.config["SECRET_KEY"])
        # verifies token is valid and has not expired
        try:
            data = s.loads(token)
        except:
            return False
        # Checks token's id against logged in user, stored in current_app
        # a malicious user cannot confirm someone elses account
        if data.get("confirm") != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True
    
    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute.")
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({"reset": self.id})
        
    def reset_password(self, token, new_password):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get("reset") != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True
        
    def generate_email_change_token(self, new_email, expiration=3600):
            s = Serializer(current_app.config['SECRET_KEY'], expiration)
            return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(self.email.encode("utf-8")).hexdigest()
        db.session.add(self)
        return True
    
    def can(self, permissions):
        # Performs a bitwise and operation between the requested permissions and assigned permissions
        # method returns true if all requested permissions are present in the role
        return self.role is not None and (self.role.permissions & permissions) == permissions
        
    def is_administrator(self):
        # Helper function that checks for admin permissions as it is very common
        return self.can(Permission.ADMINISTER)
    
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
    
    def gravatar(self, size=180, default="identicon", rating="g"):
        # Matches the security of the client request
        if request.is_secure:
            url = "https://secure.gravatar.com/avatar"
        else:
            url = "http://www.gravatar.com/avatar"
        # Uses cached version if it exists
        hash = self.avatar_hash or hashlib.md5(self.email.encode("utf-8")).hexdigest()
        return "{url}/{hash}?s={size}&d={default}&r={rating}".format(
            url=url, hash=hash, size=size, default=default, rating=rating)
        
    def __repr__(self):
        return "<User %r>" % self.username

class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80
    
    
class AnonymousUser(AnonymousUserMixin):
    # Custom anonymous user class so can and is_administrator methods can be called on all current_user objects
    def can(self, permissions):
        return False
    
    def is_administrator(self):
        return False
    
# Need to regiser the new custom anonymous user class with the login manager
login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    """Required callback function for login manager to load a user 
    (user_id is supplied as a Unicode string)
    User is loaded into current_user"""
    return User.query.get(int(user_id))

# New model that represents posts
class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    


