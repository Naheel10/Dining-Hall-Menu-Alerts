# UW–Madison Dining Hall Menu Alerts

Production-style Flask web app that lets users track favorite dining items and receive email alerts when those items show up on UW–Madison Nutrislice menus.

## Features

- User auth: signup/login/logout with hashed passwords
- Dashboard with saved favorites
- Dining hall + meal preferences
- Notification frequency preference storage
- Manual “Check menus now” trigger from dashboard
- Background-compatible menu checker for all users
- SMTP email alerts with HTML + text fallback
- Nutrislice client abstraction for menu lookups
- SQLite local development; PostgreSQL-ready via `DATABASE_URL`
- Dockerized deployment with Gunicorn
- Pytest coverage for matching, email formatting, and auth flow

## Tech Stack

- **Backend:** Flask, Python 3.11
- **ORM/DB:** SQLAlchemy (`Flask-SQLAlchemy`)
- **Frontend:** Jinja templates + Bootstrap 5
- **Email:** SMTP (`smtplib`)
- **Testing:** pytest
- **Container:** Docker (+ optional docker-compose)

## Project Structure

```text
.
├── app/
│   ├── __init__.py
│   ├── __main__.py
│   ├── config.py
│   ├── models.py
│   ├── services/
│   │   ├── email_service.py
│   │   ├── menu_matcher.py
│   │   └── nutrislice_client.py
│   └── templates/
│       ├── base.html
│       ├── dashboard.html
│       ├── index.html
│       ├── login.html
│       └── signup.html
├── tests/
│   ├── conftest.py
│   ├── test_auth_routes.py
│   ├── test_email_format.py
│   └── test_matching.py
├── app.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Nutrislice Integration Design

Nutrislice-specific API behavior is isolated in `app/services/nutrislice_client.py`:

- `get_locations()`
- `get_menu_for_date_and_location(date, location_id)`
- `normalize_item_name(name)`

This keeps scraping/API logic separate from business logic.

## Environment Variables

Create a `.env` file locally (do **not** commit it):

```bash
FLASK_ENV=development
SECRET_KEY=replace-me
DATABASE_URL=sqlite:///menu_alerts.db

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com

MENU_LOOKAHEAD_DAYS=3
```

### Notes

- Default DB fallback is SQLite when `DATABASE_URL` is unset.
- For PostgreSQL, use: `DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/dbname`

## Local Development (without Docker)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app.py
flask run
```

Open: `http://127.0.0.1:5000`

## Run Menu Check Jobs

### Manual CLI

```bash
python -m app run_menu_check
# or
flask run_menu_check
```

### Example Cron (every morning at 7:00 AM)

```cron
0 7 * * * cd /path/to/repo && /usr/bin/python3 -m app run_menu_check >> menu-check.log 2>&1
```

## Running Tests

```bash
pytest
```

## Docker Usage

### Build and run locally

```bash
docker build -t uw-dining-alerts:latest .
docker run --env-file .env -p 5000:5000 uw-dining-alerts:latest
```

### Optional docker-compose

```bash
docker compose up --build
```

## Deploying to AWS EC2 with Docker (Ubuntu)

1. **Build and push image from local machine:**
   ```bash
   docker build -t <dockerhub-user>/uw-dining-alerts:latest .
   docker push <dockerhub-user>/uw-dining-alerts:latest
   ```

2. **Launch EC2 Ubuntu instance:**
   - Open inbound security group ports: `22`, `80`, `443` (and optionally `5000` for direct app testing)

3. **Install Docker on EC2:**
   ```bash
   sudo apt-get update
   sudo apt-get install -y ca-certificates curl gnupg
   sudo install -m 0755 -d /etc/apt/keyrings
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
   echo \
     "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
     $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" | \
     sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   sudo apt-get update
   sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
   sudo usermod -aG docker ubuntu
   ```

4. **Pull and run your app image on EC2:**
   ```bash
   docker pull <dockerhub-user>/uw-dining-alerts:latest
   docker run -d --name uw-dining-alerts \
     -p 5000:5000 \
     -e SECRET_KEY='strong-secret' \
     -e DATABASE_URL='sqlite:///menu_alerts.db' \
     -e SMTP_HOST='smtp.gmail.com' \
     -e SMTP_PORT='587' \
     -e SMTP_USER='your-email@gmail.com' \
     -e SMTP_PASSWORD='your-app-password' \
     -e FROM_EMAIL='your-email@gmail.com' \
     <dockerhub-user>/uw-dining-alerts:latest
   ```

5. **Recommended next step:**
   - Put Nginx in front of the container for TLS termination and cleaner production routing.

## Security and Production Notes

- Always use a strong `SECRET_KEY`.
- Use app passwords or provider-specific SMTP credentials.
- For true production scale, move scheduling to a worker/queue + managed DB.

