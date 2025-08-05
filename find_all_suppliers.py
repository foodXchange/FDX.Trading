import os
import sys

# Fix Windows encoding
sys.stdout.reconfigure(encoding='utf-8')

print("🔍 Searching for possible database connections...\n")

# Check various .env files
env_files = [
    ".env",
    ".env.local",
    ".env.production",
    "deploy/.env",
    "app/.env"
]

for env_file in env_files:
    if os.path.exists(env_file):
        print(f"📄 Found {env_file}:")
        with open(env_file, 'r') as f:
            for line in f:
                if 'DATABASE_URL' in line or 'POSTGRES' in line:
                    print(f"   {line.strip()}")

# Check if there's an old database URL
print("\n🔍 Checking for other PostgreSQL servers in Azure...")

# Common Azure PostgreSQL patterns
possible_servers = [
    "foodxchange-db",
    "foodxchange-flex-db",
    "fdx-postgres-server",
    "foodxchange-postgres",
    "fdx-db"
]

print("\n💡 Possible database locations:")
print("1. Current: fdx-postgres-server.postgres.database.azure.com (6,088 suppliers)")
print("2. Old server might be: foodxchange-flex-db.postgres.database.azure.com")
print("3. Check Azure Portal for all PostgreSQL servers")
print("\n📱 The app at http://4.206.1.15:8003 might use a different database")
print("   or the data might be cached/stored differently")