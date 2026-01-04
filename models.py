"""Database models for FixMe pixel art platform."""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Project(db.Model):
    """Represents a pixel art project."""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    original_image_url = db.Column(db.String(500))
    width = db.Column(db.Integer, default=100)
    height = db.Column(db.Integer, default=100)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    pixels = db.relationship('PixelHistory', backref='project', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'original_image_url': self.original_image_url,
            'width': self.width,
            'height': self.height,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class PixelHistory(db.Model):
    """Stores the history of pixel modifications."""
    __tablename__ = 'pixel_history'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    x = db.Column(db.Integer, nullable=False)
    y = db.Column(db.Integer, nullable=False)
    red = db.Column(db.Integer, nullable=False)
    green = db.Column(db.Integer, nullable=False)
    blue = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.String(100))
    payment_id = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'x': self.x,
            'y': self.y,
            'red': self.red,
            'green': self.green,
            'blue': self.blue,
            'user_id': self.user_id,
            'payment_id': self.payment_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class User(db.Model):
    """Represents a user session."""
    __tablename__ = 'users'
    
    id = db.Column(db.String(100), primary_key=True)
    email = db.Column(db.String(200))
    total_pixels = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'total_pixels': self.total_pixels,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
