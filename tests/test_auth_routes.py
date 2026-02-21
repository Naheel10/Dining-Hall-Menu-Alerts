from app.models import User


def test_signup_and_login_flow(client, app_instance):
    signup_response = client.post(
        "/signup",
        data={"email": "new@wisc.edu", "password": "password123"},
        follow_redirects=True,
    )
    assert b"Account created" in signup_response.data

    with app_instance.app_context():
        user = User.query.filter_by(email="new@wisc.edu").first()
        assert user is not None
        assert user.password_hash != "password123"

    login_response = client.post(
        "/login",
        data={"email": "new@wisc.edu", "password": "password123"},
        follow_redirects=True,
    )
    assert b"Dashboard" in login_response.data
