from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
import json
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    """Пользователь с аутентификацией"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    telegram_id = db.Column(db.String(64), unique=True, nullable=True)  # Может быть None
    password_hash = db.Column(db.String(256))  # Для веб-входа
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связи (только свои данные)
    categories = db.relationship('Category', backref='user', lazy=True, cascade='all, delete-orphan')
    events = db.relationship('Event', backref='user', lazy=True, cascade='all, delete-orphan')
    templates = db.relationship('Template', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password) if self.password_hash else False
    
    def __repr__(self):
        return f'<User {self.username}>'

class Category(db.Model):
    """Категории пользователя"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(7), default='#007bff')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связь с событиями (только конкретного пользователя)
    events = db.relationship('Event', backref='category', lazy=True)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'name', name='unique_category_per_user'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            # 'code': self.code,  ← пока нет, добавим позже
        }
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Event(db.Model):
    """События пользователя"""
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'plan' или 'fact'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    source = db.Column(db.String(20), default='web')  # 'web' или 'telegram'
    
    # Индексы
    __table_args__ = (
        db.Index('idx_event_user', 'user_id'),
        db.Index('idx_event_user_time', 'user_id', 'start_time'),
    )
    
    def __repr__(self):
        return f'<Event {self.type} {self.start_time}>'

    def to_dict(self):
        return {
            'id': self.id,
            'category_id': self.category_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'type': self.type,  # 'plan' или 'fact'
            'source': self.source,  # 'web' или 'telegram'
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Template(db.Model):
    """Шаблоны пользователя"""
    __tablename__ = 'templates'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    data = db.Column(db.JSON, nullable=False)  # JSON структура
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Template {self.name}>'
