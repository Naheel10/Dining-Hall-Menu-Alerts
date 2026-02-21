"""Nutrislice client for UW-Madison dining menus."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import logging
import re

import requests

LOGGER = logging.getLogger(__name__)

BASE_URL = "https://wisc-housingdining.nutrislice.com"
API_LOCATIONS_URL = f"{BASE_URL}/api/menu/api/sites/"
API_MENU_URL_TEMPLATE = (
    f"{BASE_URL}/api/menu/api/weeks/school/{{location_id}}/menu-type/{{menu_type_id}}/{{iso_date}}/"
)
DEFAULT_MENU_TYPE_ID = 1714


@dataclass
class MenuItem:
    name: str
    normalized_name: str
    meal: str
    date: date
    dining_hall: str


def normalize_item_name(name: str) -> str:
    """Normalize menu names for case-insensitive and whitespace-tolerant matching."""
    compact = re.sub(r"\s+", " ", name.strip().lower())
    return re.sub(r"[^a-z0-9 ]", "", compact)


class NutrisliceClient:
    """Client for Nutrislice public JSON endpoints."""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def get_locations(self) -> list[dict]:
        response = requests.get(API_LOCATIONS_URL, timeout=self.timeout)
        response.raise_for_status()
        payload = response.json()
        locations = payload.get("objects", payload if isinstance(payload, list) else [])
        return [
            {"id": loc.get("id"), "name": loc.get("name", "Unknown")}
            for loc in locations
            if loc.get("id")
        ]

    def get_menu_for_date_and_location(self, target_date: date, location_id: int) -> list[MenuItem]:
        """Return structured menu items for a date and location."""
        iso_date = target_date.isoformat()
        url = API_MENU_URL_TEMPLATE.format(
            location_id=location_id, menu_type_id=DEFAULT_MENU_TYPE_ID, iso_date=iso_date
        )
        response = requests.get(url, timeout=self.timeout)
        if response.status_code == 404:
            LOGGER.warning("Menu not found for location_id=%s on date=%s", location_id, iso_date)
            return []
        response.raise_for_status()
        payload = response.json()

        dining_hall_name = payload.get("site_name", f"Location {location_id}")
        items: list[MenuItem] = []

        for day in payload.get("days", []):
            for meal in day.get("menu_items", []):
                meal_name = meal.get("meal", "Unknown")
                for item in meal.get("items", []):
                    item_name = item.get("name", "")
                    if not item_name:
                        continue
                    items.append(
                        MenuItem(
                            name=item_name,
                            normalized_name=normalize_item_name(item_name),
                            meal=meal_name,
                            date=target_date,
                            dining_hall=dining_hall_name,
                        )
                    )
        return items
