from app.services.email_service import build_match_email_content


def test_build_match_email_content_structure():
    matches = [
        {
            "favorite_item_name": "Pizza",
            "menu_item_name": "Cheese Pizza",
            "dining_hall": "Gordon Avenue Market",
            "meal": "Lunch",
            "menu_date": "2026-02-01",
        }
    ]

    subject, html_body, text_body = build_match_email_content(
        "student@wisc.edu", matches, "http://localhost:5000/dashboard"
    )

    assert "UW–Madison dining alert" in subject
    assert "<table" in html_body
    assert "Cheese Pizza" in html_body
    assert "Dashboard" in text_body
