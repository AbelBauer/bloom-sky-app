from datetime import datetime
import functools, json, os, smtplib
from email.message import EmailMessage
import getpass, time

class ApiLimiter:
    def __init__(self, max_calls=5000, filepath="api_calls.json"):
        self.max_calls = max_calls
        self.call_timestamps = []
        self.alert_threshold = 0.8
        self.alert_sent = False
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
            self.alert_sent = False
        return len(self.filter_calls_this_month()) < self.max_calls

    def record_call(self):
        if self.can_call():
            self.call_timestamps.append(datetime.now())
            self.save()

            if self.usage_ratio() >= self.alert_threshold and not self.alert_sent:
                self.send_alert()
                self.alert_sent = True

            return True
        return False

    def guard(self, fallback=None, error_message="Monthly API limit reached"):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if self.can_call():
                    self.record_call()
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
        msg['Subject'] = f'API Usage Alert – {remaining} Calls Left'
        msg['From'] = 'abelnuovo@gmail.com'
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

    def clear_credentials(self):
        self._cached_credentials = None
