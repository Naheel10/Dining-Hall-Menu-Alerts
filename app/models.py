"""Database models for menu alerts."""

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()


class User(db.Model):
    """Application user."""

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    dining_halls = db.Column(db.Text, default="")
    meals = db.Column(db.Text, default="")
    notification_frequency = db.Column(db.String(50), default="once_per_day")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    favorites = db.relationship(
        "Favorite", backref="user", cascade="all, delete-orphan", lazy=True
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def dining_halls_list(self) -> list[str]:
        return [item for item in self.dining_halls.split(",") if item]

    def meals_list(self) -> list[str]:
        return [item for item in self.meals.split(",") if item]


class Favorite(db.Model):
    """User favorite menu item by free text name."""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    item_name = db.Column(db.String(255), nullable=False)
    normalized_name = db.Column(db.String(255), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class MenuMatch(db.Model):
    """A discovered menu match for a user."""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    favorite_item_name = db.Column(db.String(255), nullable=False)
    menu_item_name = db.Column(db.String(255), nullable=False)
    dining_hall = db.Column(db.String(255), nullable=False)
    meal = db.Column(db.String(255), nullable=True)
    menu_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
