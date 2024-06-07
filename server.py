from database import get_db

db = get_db()
if db is None:
    print("Failed to get database.")
else:
    print("Database connected successfully.")