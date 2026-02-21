from app.models import Favorite, User


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
    assert b"Your Dining Alerts Dashboard" in login_response.data


def test_public_landing_and_authenticated_redirect(client):
    public_home = client.get("/")
    assert b"Never miss your favorite dining hall meals again" in public_home.data

    client.post(
        "/signup",
        data={"email": "redirect@wisc.edu", "password": "password123"},
        follow_redirects=True,
    )
    client.post(
        "/login",
        data={"email": "redirect@wisc.edu", "password": "password123"},
        follow_redirects=True,
    )

    redirected_home = client.get("/", follow_redirects=True)
    assert b"Your Dining Alerts Dashboard" in redirected_home.data


def test_demo_login_creates_seeded_user(client, app_instance):
    response = client.get("/demo-login", follow_redirects=True)
    assert b"exploring the demo account" in response.data
    assert b"Mac &amp; Cheese" in response.data

    with app_instance.app_context():
        demo_user = User.query.filter_by(email="demo@demo.com").first()
        assert demo_user is not None
        assert demo_user.dining_halls
        assert demo_user.meals
        assert Favorite.query.filter_by(user_id=demo_user.id).count() >= 3
