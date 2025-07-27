# Optimized Sentry configuration
import os

# Sentry configuration optimized for production
SENTRY_CONFIG = {
    "dsn": os.getenv("SENTRY_DSN", ""),
    "environment": os.getenv("SENTRY_ENVIRONMENT", "development"),
    "traces_sample_rate": float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
    "profiles_sample_rate": float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1")),
    "send_default_pii": False,
    "before_send": lambda event, hint: event,
} 