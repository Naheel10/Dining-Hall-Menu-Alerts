"""Flask application factory."""

from __future__ import annotations

import logging
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, url_for

from app.config import Config
from app.models import Favorite, MenuMatch, User, db
from app.services.email_service import EmailClient
from app.services.menu_matcher import run_menu_check_for_all_users, run_menu_check_for_user
from app.services.nutrislice_client import normalize_item_name

load_dotenv()
logging.basicConfig(level=logging.INFO)

DEFAULT_DINING_HALLS = [
    "Gordon Avenue Market",
    "Four Lakes Market",
    "Rheta's Market",
    "Liz's Market",
]
DEFAULT_MEALS = ["Breakfast", "Lunch", "Dinner"]
DEMO_EMAIL = "demo@demo.com"
DEMO_FAVORITES = ["Mac & Cheese", "Spicy Chicken Sandwich", "Cheese Curds"]


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    db.init_app(app)

    if app.config["SMTP_HOST"] and app.config["FROM_EMAIL"]:
        app.extensions["email_client"] = EmailClient(
            smtp_host=app.config["SMTP_HOST"],
            smtp_port=app.config["SMTP_PORT"],
            smtp_user=app.config["SMTP_USER"],
            smtp_password=app.config["SMTP_PASSWORD"],
            from_email=app.config["FROM_EMAIL"],
        )

    with app.app_context():
        db.create_all()

    register_routes(app)
    register_cli(app)
    return app


def current_user() -> User | None:
    uid = session.get("user_id")
    if not uid:
        return None
    return User.query.get(uid)


def _seed_demo_user(demo_user: User) -> None:
    """Seed default visual data so recruiters can explore an interesting dashboard."""
    if not demo_user.dining_halls:
        demo_user.dining_halls = ",".join(DEFAULT_DINING_HALLS[:3])
    if not demo_user.meals:
        demo_user.meals = ",".join(DEFAULT_MEALS)
    if not demo_user.notification_frequency:
        demo_user.notification_frequency = "once_per_day"

    existing_names = {fav.item_name for fav in Favorite.query.filter_by(user_id=demo_user.id).all()}
    for item_name in DEMO_FAVORITES:
        if item_name in existing_names:
            continue
        db.session.add(
            Favorite(
                user_id=demo_user.id,
                item_name=item_name,
                normalized_name=normalize_item_name(item_name),
            )
        )


def register_routes(app: Flask) -> None:
    @app.context_processor
    def inject_user():
        return {"current_user": current_user()}

    @app.get("/")
    def index():
        user = current_user()
        if user:
            return redirect(url_for("dashboard"))
        return render_template("index.html")

    @app.get("/demo-login")
    def demo_login():
        demo_user = User.query.filter_by(email=DEMO_EMAIL).first()

        if not demo_user:
            demo_user = User(
                email=DEMO_EMAIL,
                dining_halls=",".join(DEFAULT_DINING_HALLS[:3]),
                meals=",".join(DEFAULT_MEALS),
                notification_frequency="once_per_day",
            )
            # Recruiter/demo account: this user can be auto-logged in to showcase the product UX.
            # We still set a password hash so the account is structurally identical to normal users.
            demo_user.set_password("demo-account-safe-default")
            db.session.add(demo_user)
            db.session.flush()

        _seed_demo_user(demo_user)
        db.session.commit()

        # This route is intentionally passwordless only for the single demo account above.
        session["user_id"] = demo_user.id
        flash("You are now exploring the demo account dashboard.", "success")
        return redirect(url_for("dashboard"))

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            if not email or not password:
                flash("Email and password are required.", "danger")
                return render_template("signup.html")
            if User.query.filter_by(email=email).first():
                flash("An account with that email already exists.", "danger")
                return render_template("signup.html")

            user = User(email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Account created. Please log in.", "success")
            return redirect(url_for("login"))
        return render_template("signup.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            user = User.query.filter_by(email=email).first()
            if not user or not user.check_password(password):
                flash("Invalid credentials.", "danger")
                return render_template("login.html")
            session["user_id"] = user.id
            flash("Welcome back!", "success")
            return redirect(url_for("dashboard"))
        return render_template("login.html")

    @app.get("/logout")
    def logout():
        session.clear()
        flash("Logged out.", "info")
        return redirect(url_for("index"))

    @app.route("/dashboard", methods=["GET", "POST"])
    def dashboard():
        user = current_user()
        if not user:
            return redirect(url_for("login"))

        if request.method == "POST":
            action = request.form.get("action")
            if action == "add_favorite":
                item = request.form.get("item_name", "").strip()
                if item:
                    db.session.add(
                        Favorite(
                            user_id=user.id,
                            item_name=item,
                            normalized_name=normalize_item_name(item),
                        )
                    )
                    db.session.commit()
                    flash("Favorite added.", "success")
                else:
                    flash("Favorite name cannot be empty.", "danger")
            elif action == "delete_favorite":
                fav_id = request.form.get("favorite_id", type=int)
                favorite = Favorite.query.filter_by(id=fav_id, user_id=user.id).first()
                if favorite:
                    db.session.delete(favorite)
                    db.session.commit()
                    flash("Favorite removed.", "info")
            elif action == "update_preferences":
                halls = request.form.getlist("dining_halls")
                meals = request.form.getlist("meals")
                frequency = request.form.get("notification_frequency", "once_per_day")
                user.dining_halls = ",".join(halls)
                user.meals = ",".join(meals)
                user.notification_frequency = frequency
                db.session.commit()
                flash("Preferences updated.", "success")
            elif action == "manual_check":
                matches = run_menu_check_for_user(user.id, send_email=True)
                user.last_checked_at = datetime.utcnow()
                db.session.commit()
                flash(f"Manual check complete. Found {len(matches)} matches.", "success")
            return redirect(url_for("dashboard"))

        favorites = Favorite.query.filter_by(user_id=user.id).order_by(Favorite.created_at.desc()).all()
        upcoming_matches = (
            MenuMatch.query.filter_by(user_id=user.id)
            .order_by(MenuMatch.menu_date.asc(), MenuMatch.created_at.desc())
            .limit(25)
            .all()
        )

        return render_template(
            "dashboard.html",
            user=user,
            favorites=favorites,
            dining_halls_options=DEFAULT_DINING_HALLS,
            meal_options=DEFAULT_MEALS,
            upcoming_matches=upcoming_matches,
        )


def register_cli(app: Flask) -> None:
    @app.cli.command("run_menu_check")
    def run_menu_check_command() -> None:
        """CLI entry point for cron-triggered checks."""
        summary = run_menu_check_for_all_users(send_email=True)
        print(f"Menu check complete: {summary}")
