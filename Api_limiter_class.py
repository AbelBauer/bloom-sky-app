"""
ApiLimiter

A quota-aware API usage manager for personal Python applications. Designed to track and enforce both monthly and daily API call limits, 
with built-in alerting via Gmail and persistent usage logging.

This class is ideal for projects that rely on third-party APIs with strict usage quotas, such as Bloom and Sky. It ensures responsible API consumption, 
notifies the user when usage crosses key thresholds, and provides daily email summaries once usage becomes significant.

Features:
---------
- Tracks API call timestamps persistently across sessions using a JSON file.
- Enforces monthly and daily call limits via 'can_call()' and 'guard()' decorator.
- CLI notification when 50% of monthly quota is reached.
- Begins sending daily Gmail alerts once 50% threshold is crossed.
- Sends a one-time Gmail alert when usage exceeds a configurable threshold (default: 80%).
- Prompts for Gmail credentials interactively and caches them securely in memory.
- Prevents duplicate daily alerts using a local flag file.

Parameters:
-----------
max_calls : int
    Maximum number of API calls allowed per calendar month.
daily_max_calls : int
    Maximum number of API calls allowed per calendar day.
filepath : str
    Path to the JSON file used to store API call timestamps.

Usage:
------
# Instantiate limiter
limiter = ApiLimiter(max_calls=5000, daily_max_calls=100)

# Decorate any function that makes an API call
@limiter.guard(fallback=None)
def get_current_weather(lat, lon):
    ...

# Check quota manually
if limiter.can_call():
    limiter.record_call()
    ...

# View usage summary
print(limiter)

Email Provider Compatibility:
-----------------------------
This alert system is currently designed to work **exclusively with Gmail**, using Gmail's SMTP server and app-specific passwords. 
No other email providers are supported at this time.

If the project scales up or is adapted for broader use, future versions may include support for other popular providers such as Outlook, Yahoo, and custom domains.

Design Notes:
-------------
- Uses ISO-formatted datetime strings for portability and clarity.
- Monthly usage resets automatically when a new month begins.
- Daily alerts are triggered only after 50% of monthly quota is reached, reducing noise.
- Email alerts are sent using Gmail SMTP with app-specific passwords.
- No credentials are stored on disk; all authentication is handled securely at runtime.

Limitations:
------------
- Requires internet access and valid Gmail credentials to send alerts.
- Assumes local system time is accurate for quota tracking.
- Alert emails may fail silently if SMTP login fails or credentials are incorrect.

Author:
-------
abelnuovo@gmail.com - Bloom and Sky Project
"""

from datetime import datetime
import functools, json, os, smtplib
from email.message import EmailMessage
import getpass, time

class ApiLimiter:
    def __init__(self, max_calls=5000, daily_max_calls=1000, alert_treshold=0.5, filepath="api_calls.json"):
        self._max_calls = max_calls
        self._daily_max_calls = daily_max_calls
        self.call_timestamps = []
        self.alert_threshold = alert_treshold
        self.alert_sent = False
        self.daily_alert_active = False
        self.alert_email = 'abelnuovo@gmail.com'
        self._cached_credentials = None
        self.filepath = filepath
        self.load(filepath)

    def __str__(self):
        calls_this_month = self.filter_calls_this_month()
        calls_left = self.max_calls - len(calls_this_month)
        return (f"Calls left: {calls_left} out of {self.max_calls} "
                f"this month ({datetime.now().strftime('%B %Y')})")

    def filter_calls_this_month(self):
        now = datetime.now()
        return [ts for ts in self.call_timestamps
                if ts.year == now.year and ts.month == now.month]

    def is_same_month(self, dt1, dt2):
        return dt1.year == dt2.year and dt1.month == dt2.month

    def can_call(self):
        if self.call_timestamps and not self.is_same_month(self.call_timestamps[-1], datetime.now()):
            self.call_timestamps = []
            self.alert_sent = False # Reset monthly alert

        if self.call_timestamps and not self.is_same_month(self.call_timestamps[-1], datetime.now()):
            self.call_timestamps = []
            self.alert_sent = False
            self.daily_alert_active = False  # Reset daily alert

        return len(self.filter_calls_this_month()) < self.max_calls

    def record_call(self):
        if self.can_call():
            self.call_timestamps.append(datetime.now())
            self.save()

            # CLI notification at 50% usage
            if self.usage_ratio() >= 0.5 and not self.daily_alert_active:
                print(f"⚠️ API usage has reached 50% of monthly quota ({self.max_calls}).")
                self.daily_alert_active = True

            # Start sending daily alerts once 50% is reached
            if self.daily_alert_active and not self.alert_sent_today():
                self.send_daily_usage_alert()
                self.mark_alert_sent_today()

            # Optional: still send one-time alert at 80%
            if self.usage_ratio() >= self.alert_threshold and not self.alert_sent:
                self.send_alert()
                self.alert_sent = True

            return True
        return False
    
    @property
    def max_calls(self):
        return self._max_calls
    @max_calls.setter
    def max_calls(self, value):
        if not isinstance(value, int):
            raise TypeError("'Max. Calls' should be an integer.")
        if value > 5000:
            raise ValueError("'Max. Calls' value should'nt exceed 5000.")
        
    @property
    def daily_max_calls(self):
        return self._daily_max_calls
    @daily_max_calls.setter
    def daily_max_calls(self, value):
        if not isinstance(value, int):
            raise TypeError("'Daily Max. Calls' should be an integer.")
        if value > 1000:
            raise ValueError("'Daily Max. Calls' value should'nt exceed 100.")

    def guard(self, fallback=None, error_message="API quota reached!"):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if self.can_call():
                    return func(*args, **kwargs)
                if fallback is not None:
                    return fallback
                raise RuntimeError(error_message)
            return wrapper
        return decorator

    def save(self):
        data = [dt.isoformat() for dt in self.call_timestamps]
        with open(self.filepath, 'w') as f:
            json.dump(data, f)

    def load(self, filepath):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.call_timestamps = [datetime.fromisoformat(ts) for ts in data]
        except FileNotFoundError:
            self.call_timestamps = []

    def usage_ratio(self):
        return len(self.filter_calls_this_month()) / self.max_calls

    def get_credentials(self):
        if self._cached_credentials:
            return self._cached_credentials

        print("🔐 Gmail login required to send alert email.")
        email = input("Enter your Gmail address: ")
        password = getpass.getpass("Enter your Gmail app password: ")

        if not email or not password:
            raise ValueError("Email and password must not be empty.")

        self._cached_credentials = (email, password)
        return self._cached_credentials

    def send_alert(self, retries=3, delay=2):
        used = len(self.filter_calls_this_month())
        remaining = self.max_calls - used
        usage_percent = self.usage_ratio() * 100
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        msg = EmailMessage()
        msg.set_content(
            f"⚠️ API usage alert:\n"
            f"- Timestamp: {timestamp}\n"
            f"- {usage_percent:.1f}% of monthly quota used\n"
            f"- {remaining} calls remaining out of {self.max_calls}\n"
            f"- Month: {datetime.now().strftime('%B %Y')}\n"
        )
        msg['Subject'] = f'API Usage Alert. {remaining} Calls Left'
        msg['From'] = self.get_credentials()[0]
        msg['To'] = self.alert_email

        user, pwd = self.get_credentials()

        for attempt in range(1, retries + 1):
            try:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(user, pwd)
                    smtp.send_message(msg)
                print("✅ Alert email sent successfully.")
                return
            except Exception as e:
                print(f"❌ Attempt {attempt} failed: {e}")
                if attempt < retries:
                    time.sleep(delay)

        print("🚫 All attempts to send alert failed.")

    def send_daily_usage_alert(self):
        used_today = len(self.filter_calls_today())
        remaining_today = self.daily_max_calls - used_today
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        msg = EmailMessage()
        msg.set_content(
            f"🌤️ Daily API Usage Report:\n"
            f"- Timestamp: {timestamp}\n"
            f"- Calls used today: {used_today}\n"
            f"- Remaining today: {remaining_today}\n"
            f"- Daily limit: {self.daily_max_calls}\n"
        )
        msg['Subject'] = f'Daily API Usage. {used_today} Calls Used'
        user, pwd = self.get_credentials()
        msg['From'] = user
        msg['To'] = self.alert_email

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(user, pwd)
                smtp.send_message(msg)
            print("📬 Daily usage alert sent.")
        except Exception as e:
            print(f"❌ Failed to send daily alert: {e}")

    def alert_sent_today(self):
        try:
            with open("daily_alert_flag.json", "r") as f:
                data = json.load(f)
                return data.get("date") == datetime.now().strftime("%Y-%m-%d")
        except FileNotFoundError:
            return False

    def mark_alert_sent_today(self):
        with open("daily_alert_flag.json", "w") as f:
            json.dump({"date": datetime.now().strftime("%Y-%m-%d")}, f)

    def clear_credentials(self):
        self._cached_credentials = None

    def filter_calls_today(self):
        now = datetime.now()
        return [ts for ts in self.call_timestamps
                if ts.year == now.year and ts.month == now.month and ts.day == now.day]

