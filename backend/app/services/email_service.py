import logging

import requests
from flask import current_app

logger = logging.getLogger(__name__)

BREVO_SEND_URL = "https://api.brevo.com/v3/smtp/email"


class EmailService:
    """Thin wrapper around Brevo's transactional email API.

    Deliberately fails soft: if BREVO_API_KEY isn't configured or the API
    call fails, we log it and return False rather than raising - a broken
    email provider should never break registration, login, or password
    reset for the user.
    """

    def send(self, to_email, subject, html_content):
        api_key = current_app.config["BREVO_API_KEY"]
        if not api_key:
            logger.warning("BREVO_API_KEY not configured - skipping email to %s: %s", to_email, subject)
            return False

        payload = {
            "sender": {
                "name": current_app.config["MAIL_FROM_NAME"],
                "email": current_app.config["MAIL_FROM_EMAIL"],
            },
            "to": [{"email": to_email}],
            "subject": subject,
            "htmlContent": html_content,
        }
        headers = {
            "api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            response = requests.post(BREVO_SEND_URL, json=payload, headers=headers, timeout=10)
            if response.status_code >= 300:
                logger.error("Brevo send failed (%s): %s", response.status_code, response.text)
                return False
            return True
        except requests.RequestException:
            logger.exception("Brevo send raised an exception")
            return False

    def send_password_reset(self, to_email, reset_link):
        html = f"""
        <p>We received a request to reset your Karmvikas HR password.</p>
        <p><a href="{reset_link}">Click here to reset your password</a> — this link expires in 30 minutes.</p>
        <p>If you didn't request this, you can safely ignore this email.</p>
        """
        return self.send(to_email, "Reset your Karmvikas HR password", html)

    def send_welcome(self, to_email, first_name):
        login_url = current_app.config["FRONTEND_URL"] + "/login"
        html = f"""
        <p>Hi {first_name},</p>
        <p>Your Karmvikas HR account has been created. Sign in at
        <a href="{login_url}">{login_url}</a> using the email and password your HR team provided,
        or use "Forgot password" to set your own.</p>
        """
        return self.send(to_email, "Welcome to Karmvikas HR", html)
