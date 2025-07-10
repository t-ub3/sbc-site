from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='tenant')  # admin or tenant
    role_title = db.Column(db.String(100), default='Reporter')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to articles
    articles = db.relationship('Article', backref='author', lazy=True)
    
    def is_admin(self):
        return self.role == 'admin'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to articles
    articles = db.relationship('Article', backref='category', lazy=True)

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to articles
    articles = db.relationship('Article', backref='department', lazy=True)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text)  # Optional summary/excerpt
    published = db.Column(db.Boolean, default=False)
    is_breaking = db.Column(db.Boolean, default=False)
    breaking_message = db.Column(db.String(200))  # Custom breaking news message
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
    
    def __repr__(self):
        return f'<Article {self.title}>'
