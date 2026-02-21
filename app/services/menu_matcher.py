"""Menu matching and alert orchestration."""

from __future__ import annotations

from datetime import date, timedelta
import logging

from flask import current_app, url_for

from app.models import Favorite, MenuMatch, User, db
from app.services.email_service import build_match_email_content
from app.services.nutrislice_client import NutrisliceClient, normalize_item_name

LOGGER = logging.getLogger(__name__)


def find_matches_for_user(user: User, menus: list[dict], favorites: list[Favorite]) -> list[dict]:
    """Return structured matches for one user against fetched menus."""
    favorite_lookup = {fav.normalized_name: fav.item_name for fav in favorites}
    matches: list[dict] = []

    for menu in menus:
        normalized_menu = normalize_item_name(menu["name"])
        for normalized_fav, favorite_name in favorite_lookup.items():
            if normalized_fav and normalized_fav in normalized_menu:
                matches.append(
                    {
                        "favorite_item_name": favorite_name,
                        "menu_item_name": menu["name"],
                        "dining_hall": menu["dining_hall"],
                        "meal": menu.get("meal"),
                        "menu_date": menu["date"],
                    }
                )
    return matches


def _fetch_menus_for_user(user: User, lookahead_days: int) -> list[dict]:
    client = NutrisliceClient()
    locations = client.get_locations()
    selected_halls = set(user.dining_halls_list())
    selected_meals = {meal.lower() for meal in user.meals_list()}
    menus: list[dict] = []

    for offset in range(lookahead_days):
        target_date = date.today() + timedelta(days=offset)
        for location in locations:
            if selected_halls and location["name"] not in selected_halls:
                continue
            items = client.get_menu_for_date_and_location(target_date, location["id"])
            for item in items:
                if selected_meals and item.meal.lower() not in selected_meals:
                    continue
                menus.append(
                    {
                        "name": item.name,
                        "dining_hall": item.dining_hall,
                        "meal": item.meal,
                        "date": item.date,
                    }
                )
    return menus


def run_menu_check_for_user(user_id: int, send_email: bool = True) -> list[dict]:
    """Fetch menus, find matches, persist records, and optionally send email."""
    user = User.query.get(user_id)
    if not user:
        return []

    favorites = Favorite.query.filter_by(user_id=user.id).all()
    if not favorites:
        return []

    menus = _fetch_menus_for_user(user, current_app.config["MENU_LOOKAHEAD_DAYS"])
    matches = find_matches_for_user(user, menus, favorites)

    MenuMatch.query.filter_by(user_id=user.id).delete()
    for match in matches:
        db.session.add(
            MenuMatch(
                user_id=user.id,
                favorite_item_name=match["favorite_item_name"],
                menu_item_name=match["menu_item_name"],
                dining_hall=match["dining_hall"],
                meal=match["meal"],
                menu_date=match["menu_date"],
            )
        )
    db.session.commit()

    if send_email and matches and current_app.extensions.get("email_client"):
        email_client = current_app.extensions["email_client"]
        dashboard_url = url_for("dashboard", _external=True)
        subject, html_body, text_body = build_match_email_content(user.email, matches, dashboard_url)
        try:
            email_client.send_html_email(user.email, subject, html_body, text_body)
        except Exception as exc:  # noqa: BLE001
            LOGGER.exception("Failed to send alert to %s: %s", user.email, exc)

    return matches


def run_menu_check_for_all_users(send_email: bool = True) -> dict[str, int]:
    """Run checks for all users and return summary."""
    summary = {"users_checked": 0, "users_with_matches": 0, "total_matches": 0}
    for user in User.query.all():
        summary["users_checked"] += 1
        matches = run_menu_check_for_user(user.id, send_email=send_email)
        if matches:
            summary["users_with_matches"] += 1
            summary["total_matches"] += len(matches)
    return summary
