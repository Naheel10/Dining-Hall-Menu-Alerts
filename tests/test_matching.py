from app.models import Favorite, User
from app.services.menu_matcher import find_matches_for_user


def test_find_matches_case_insensitive_spacing(app_instance):
    with app_instance.app_context():
        user = User(email="user@example.com", password_hash="x")
        favorite = Favorite(user_id=1, item_name="Chicken Tikka", normalized_name="chicken tikka")
        menus = [
            {
                "name": "CHICKEN   TIKKA masala",
                "dining_hall": "Gordon Avenue Market",
                "meal": "Dinner",
                "date": "2026-01-01",
            },
            {
                "name": "Vegetable Curry",
                "dining_hall": "Four Lakes Market",
                "meal": "Lunch",
                "date": "2026-01-01",
            },
        ]

        matches = find_matches_for_user(user, menus, [favorite])

    assert len(matches) == 1
    assert matches[0]["favorite_item_name"] == "Chicken Tikka"
    assert matches[0]["dining_hall"] == "Gordon Avenue Market"
