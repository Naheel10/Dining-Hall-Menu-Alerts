import pytest

from app import create_app
from app.models import db


@pytest.fixture
def app_instance():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SECRET_KEY": "test-secret",
            "MENU_LOOKAHEAD_DAYS": 1,
        }
    )

    with app.app_context():
        db.drop_all()
        db.create_all()

    yield app


@pytest.fixture
def client(app_instance):
    return app_instance.test_client()
