# Basic Sentry configuration
import os

# Sentry configuration with defaults
SENTRY_DSN = os.getenv("SENTRY_DSN", "https://fdf092923fb6dd5351274f42e8a4dee9@o4509734929104896.ingest.de.sentry.io/4509734959775824")
SENTRY_ENVIRONMENT = os.getenv("SENTRY_ENVIRONMENT", "production")
SENTRY_TRACES_SAMPLE_RATE = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "1.0"))
SENTRY_PROFILES_SAMPLE_RATE = float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "1.0")) 