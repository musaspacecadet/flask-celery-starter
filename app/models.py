from sqlalchemy.sql import func
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app


db = SQLAlchemy()
migrate = Migrate()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=func.now())
    verified = db.Column(db.Boolean, default=False)
    verify_token = db.Column(db.String(100))
    verify_token_expiration = db.Column(db.DateTime)
    reset_token = db.Column(db.String(100))
    reset_token_expiration = db.Column(db.DateTime)

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_verify_token(self, expires_in=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in)
        return s.dumps({'user_id': self.user_id}).decode('utf-8')

    @staticmethod
    def verify_user_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def get_reset_token(self, expires_in=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in)
        return s.dumps({'reset_user_id': self.user_id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['reset_user_id']
        except:
            return None
        return User.query.get(user_id)
    
    def get_id(self):
        return str(self.user_id)


class Folder(db.Model):
    __tablename__ = 'folders'

    folder_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    folder_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=func.now())

    user = db.relationship("User", backref=db.backref("folders", cascade="all, delete-orphan"))

    def __repr__(self):
        return f"<Folder {self.folder_name}>"

class Feed(db.Model):
    __tablename__ = 'feeds'

    feed_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    folder_id = db.Column(db.Integer, db.ForeignKey('folders.folder_id', ondelete='SET NULL'))
    feed_url = db.Column(db.String(2048), nullable=False)
    feed_title = db.Column(db.String(255))
    feed_description = db.Column(db.Text)
    last_updated = db.Column(db.TIMESTAMP)
    created_at = db.Column(db.TIMESTAMP, server_default=func.now())

    user = db.relationship("User", backref=db.backref("feeds", cascade="all, delete-orphan"))
    folder = db.relationship("Folder", backref=db.backref("feeds"))

    def __repr__(self):
        return f"<Feed {self.feed_title}>"

class Post(db.Model):
    __tablename__ = 'posts'

    post_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    feed_id = db.Column(db.Integer, db.ForeignKey('feeds.feed_id', ondelete='CASCADE'), nullable=False)
    post_title = db.Column(db.String(255))
    post_link = db.Column(db.String(2048), nullable=False)
    post_description = db.Column(db.Text)
    post_content = db.Column(db.Text)
    published_at = db.Column(db.TIMESTAMP)
    created_at = db.Column(db.TIMESTAMP, server_default=func.now())

    feed = db.relationship("Feed", backref=db.backref("posts", cascade="all, delete-orphan"))

    def __repr__(self):
        return f"<Post {self.post_title}>"

class UserPost(db.Model):
    __tablename__ = 'user_posts'

    user_post_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id', ondelete='CASCADE'), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    is_starred = db.Column(db.Boolean, default=False)
    note = db.Column(db.Text)

    user = db.relationship("User", backref=db.backref("user_posts", cascade="all, delete-orphan"))
    post = db.relationship("Post", backref=db.backref("user_posts", cascade="all, delete-orphan"))

    def __repr__(self):
        return f"<UserPost user_id={self.user_id}, post_id={self.post_id}>"

class Keyword(db.Model):
    __tablename__ = 'keywords'

    keyword_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    keyword = db.Column(db.String(255), nullable=False)

    user = db.relationship("User", backref=db.backref("keywords", cascade="all, delete-orphan"))

    def __repr__(self):
        return f"<Keyword {self.keyword}>"

class PostKeyword(db.Model):
    __tablename__ = 'post_keywords'

    post_keyword_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id', ondelete='CASCADE'), nullable=False)
    keyword_id = db.Column(db.Integer, db.ForeignKey('keywords.keyword_id', ondelete='CASCADE'), nullable=False)

    post = db.relationship("Post", backref=db.backref("post_keywords", cascade="all, delete-orphan"))
    keyword = db.relationship("Keyword", backref=db.backref("post_keywords", cascade="all, delete-orphan"))

    def __repr__(self):
        return f"<PostKeyword post_id={self.post_id}, keyword_id={self.keyword_id}>"

class Tag(db.Model):
    __tablename__ = 'tags'

    tag_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    tag_name = db.Column(db.String(255), nullable=False)

    user = db.relationship("User", backref=db.backref("tags", cascade="all, delete-orphan"))

    def __repr__(self):
        return f"<Tag {self.tag_name}>"

class PostTag(db.Model):
    __tablename__ = 'post_tags'

    post_tag_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id', ondelete='CASCADE'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.tag_id', ondelete='CASCADE'), nullable=False)

    post = db.relationship("Post", backref=db.backref("post_tags", cascade="all, delete-orphan"))
    tag = db.relationship("Tag", backref=db.backref("post_tags", cascade="all, delete-orphan"))

    def __repr__(self):
        return f"<PostTag post_id={self.post_id}, tag_id={self.tag_id}>"