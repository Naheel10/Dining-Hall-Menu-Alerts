"""Email sending and formatting logic."""

from __future__ import annotations

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import smtplib

LOGGER = logging.getLogger(__name__)


class EmailClient:
    """SMTP email client for alert notifications."""

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password: str,
        from_email: str,
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_email = from_email

    def send_html_email(self, to_email: str, subject: str, html_body: str, text_body: str) -> None:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.from_email
        msg["To"] = to_email
        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            if self.smtp_user and self.smtp_password:
                server.login(self.smtp_user, self.smtp_password)
            server.sendmail(self.from_email, [to_email], msg.as_string())


def build_match_email_content(user_email: str, matches: list[dict], dashboard_url: str) -> tuple[str, str, str]:
    """Build subject and body for alert emails."""
    subject = "UW–Madison dining alert: your favorites are on the menu"

    rows = "".join(
        (
            "<tr>"
            f"<td>{match['favorite_item_name']}</td>"
            f"<td>{match['menu_item_name']}</td>"
            f"<td>{match['dining_hall']}</td>"
            f"<td>{match.get('meal') or 'N/A'}</td>"
            f"<td>{match['menu_date']}</td>"
            "</tr>"
        )
        for match in matches
    )

    html_body = f"""
    <p>Hello {user_email},</p>
    <p>Great news — your favorites are on the UW–Madison dining menu.</p>
    <table border="1" cellpadding="6" cellspacing="0">
      <thead>
        <tr>
          <th>Favorite</th><th>Menu Item</th><th>Dining Hall</th><th>Meal</th><th>Date</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
    <p>Visit your dashboard for details: <a href="{dashboard_url}">{dashboard_url}</a></p>
    """

    lines = [
        f"Hello {user_email},",
        "",
        "Your favorites are on the UW-Madison dining menu:",
    ]
    for match in matches:
        lines.append(
            f"- {match['favorite_item_name']} => {match['menu_item_name']} | "
            f"{match['dining_hall']} | {match.get('meal') or 'N/A'} | {match['menu_date']}"
        )
    lines.append("")
    lines.append(f"Dashboard: {dashboard_url}")

    return subject, html_body, "\n".join(lines)
