"""Application configuration."""

import os


class Config:
    """Default Flask configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///menu_alerts.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    FROM_EMAIL = os.getenv("FROM_EMAIL", "")

    MENU_LOOKAHEAD_DAYS = int(os.getenv("MENU_LOOKAHEAD_DAYS", "3"))
