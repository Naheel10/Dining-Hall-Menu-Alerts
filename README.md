# UW Dining Alerts

[Live Demo → uwdiningalerts.com](https://www.uwdiningalerts.com/)

UW Dining Alerts is a production-ready web app that helps UW–Madison students track favorite dining hall menu items and get notified when those meals appear.

## Why this project stands out

- **Real user value:** solves a daily student pain point (missing favorite dining meals).
- **End-to-end product:** authentication, preferences, menu ingestion, matching logic, and email delivery.
- **Production deployment:** containerized Flask app running live at **uwdiningalerts.com**.
- **Engineering practices:** modular service layer, environment-based config, and automated tests.

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
- **Database:** SQLAlchemy (SQLite locally, PostgreSQL-ready via `DATABASE_URL`)
- **Frontend:** Jinja templates, Bootstrap 5
- **Infra/Deploy:** Docker, Gunicorn
- **Testing:** pytest

## Architecture Snapshot

```text
app/
├── models.py                 # Users + favorites data model
├── services/
│   ├── nutrislice_client.py  # Menu retrieval + normalization
│   ├── menu_matcher.py       # Matching logic for favorites
│   └── email_service.py      # Alert email formatting/sending
└── templates/                # UI views
```

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app.py
flask run
```

Open `http://127.0.0.1:5000`

## Configuration

Create a `.env` file:

```bash
SECRET_KEY=replace-me
DATABASE_URL=sqlite:///menu_alerts.db
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
MENU_LOOKAHEAD_DAYS=3
```

## Run Checks + Tests

```bash
# run menu scan manually
python -m app run_menu_check

# run tests
pytest
```

## Screenshots

Screenshots from the live deployment are attached in this update (homepage, login, signup).
