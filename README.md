# UW Dining Alerts

[UWDiningalerts.com](https://www.uwdiningalerts.com/)

UW Dining Alerts is a web app that helps UW–Madison students track favorite dining hall menu items and get notified when those meals appear.

<img width="400" height="500" alt="uwdiningalerts" src="https://github.com/user-attachments/assets/6652c82b-ae95-4a35-a484-5de2fcb4d6a1" />

## Core Features

- Account signup/login/logout with secure password hashing
- Personalized favorites list for menu item tracking
- Dining hall and meal-window filtering (breakfast/lunch/dinner)
- On-demand “check menus now” trigger from the dashboard
- Scheduled/background-compatible menu checks across users
- Email alert pipeline with HTML + plain-text fallback
- Nutrislice integration isolated behind a dedicated client service

## Tech Stack

- **Backend:** Python 3.11, Flask
- **Database:** SQLAlchemy (SQLite locally, PostgreSQL production)
- **Frontend:** Jinja templates, Bootstrap 5
- **Infra/Deploy:** Docker, Gunicorn
- **Testing:** pytest

## Architecture

```text
├── app.py                        # WSGI/Gunicorn entrypoint
├── app/
│   ├── __init__.py               # App factory, routes, CLI hook registration
│   ├── config.py                 # Environment-driven config (DB, SMTP, lookahead)
│   ├── models.py                 # SQLAlchemy models: User, Favorite, MenuMatch
│   ├── services/
│   │   ├── nutrislice_client.py  # Menu retrieval + normalization
│   │   ├── menu_matcher.py       # Matching engine + scan orchestration
│   │   └── email_service.py      # Alert email composition + SMTP delivery
│   ├── templates/                # Landing, auth, dashboard views
│   └── static/css/main.css       # UI styling
└── tests/
    ├── test_auth_routes.py       # Auth + dashboard route behavior
    ├── test_matching.py          # Matching correctness
    └── test_email_format.py      # Email formatting checks
```


